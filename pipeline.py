# pipeline.py
import logging
import os
import numpy as np
import asyncio
import json
import base64
from io import BytesIO
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
from PIL import Image # Import Pillow

# FastAPI imports
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure the agents directory is in the Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from ingest import IngestAgent
from calibration import CalibrationAgent
from detection import DetectionAgent
from orbit import OrbitAgent

# --- Configuration ---
# Configure logging for the entire pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),  # Log to a file
        logging.StreamHandler(sys.stdout)     # Log to console
    ]
)
logger = logging.getLogger("Pipeline")

# FastAPI app initialization
app = FastAPI(
    title="Multi-Agent Asteroid Detection Pipeline",
    description="Backend for real-time asteroid detection and orbital analysis."
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the latest pipeline results in memory for the polling endpoint
latest_pipeline_results: Dict[str, Any] = {
    "status": "Idle",
    "filename": "N/A",
    "detections": [],
    "orbital_elements": [],
    "image_data_b64": "", # New field for Base64 image
    "error": None
}

# Initialize agents globally to avoid re-initializing on every request
ingest_agent = IngestAgent()
calibration_agent = CalibrationAgent()
detection_agent = DetectionAgent()
orbit_agent = OrbitAgent()

# Dummy FITS file path (will be created and deleted dynamically)
DUMMY_FITS_DIR = "simulated_fits_data"
os.makedirs(DUMMY_FITS_DIR, exist_ok=True)

def create_dummy_fits_file(file_path: str, observation_id: int) -> str:
    """
    Creates a dummy FITS file with slightly varied data for testing purposes.
    In a real system, this file would be ingested from a telescope.
    """
    from astropy.io import fits
    pixel_data = np.random.rand(100, 100).astype(np.float32) * 500
    for i in range(100):
        if 20 <= i < 80:
            pixel_data[i, i] += 5000
            pixel_data[i, i+1] += 2000
    
    hdu = fits.PrimaryHDU(pixel_data)
    current_utc_time = datetime.now(timezone.utc).isoformat(timespec='seconds') + 'Z'
    hdu.header['DATE'] = current_utc_time
    hdu.header['EXPTIME'] = 30.0
    hdu.header['TELESCOP'] = 'SimulatedScope'
    hdu.header['OBSERVER'] = 'AI_Pipeline'
    hdu.header['OBS_ID'] = observation_id
    try:
        hdu.writeto(file_path, overwrite=True)
        logger.info(f"Dummy FITS file created at: {file_path} (Obs ID: {observation_id})")
        return file_path
    except Exception as e:
        logger.error(f"Failed to create dummy FITS file at {file_path}: {e}")
        raise

def _numpy_to_base64_png(data: np.ndarray) -> str:
    """
    Converts a NumPy array (image data) to a Base64 encoded PNG string.
    Normalizes the data to 0-255 range.
    """
    # Normalize data to 0-255 range (for grayscale image)
    data_min = data.min()
    data_max = data.max()
    if data_max == data_min: # Handle flat images
        normalized_data = np.zeros_like(data, dtype=np.uint8)
    else:
        normalized_data = ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)
    
    # Create a PIL Image from the NumPy array
    img = Image.fromarray(normalized_data, mode='L') # 'L' for grayscale
    
    # Save image to a BytesIO object
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    # Get Base64 encoded string
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

async def run_asteroid_detection_pipeline_async(fits_file_path: str) -> Dict[str, Any]:
    """
    Asynchronously orchestrates the multi-agent asteroid detection pipeline.
    """
    global latest_pipeline_results 

    logger.info(f"Starting asteroid detection pipeline for {fits_file_path}")
    
    pipeline_run_results: Dict[str, Any] = {"status": "processing", "filename": os.path.basename(fits_file_path)}
    
    file_to_delete = fits_file_path

    try:
        logger.info("Step 1: Running Ingest Agent...")
        pixel_data, header = ingest_agent.run(fits_file_path)
        pipeline_run_results['ingested_header'] = {k: str(v) for k, v in header.items()}
        logger.info(f"Ingest Agent completed. Image dimensions: {pixel_data.shape}, Header keys: {len(header)}")

        # --- Convert pixel data to Base64 PNG for frontend display ---
        pipeline_run_results['image_data_b64'] = _numpy_to_base64_png(pixel_data)
        logger.info(f"Converted image data to Base64 PNG.")

        logger.info("Step 2: Running Calibration Agent...")
        calibrated_pixel_data, calibrated_header = calibration_agent.run(pixel_data, header)
        pipeline_run_results['calibrated_header'] = {k: str(v) for k, v in calibrated_header.items()}
        logger.info("Calibration Agent completed. Header updated with WCS info (fake).")

        logger.info("Step 3: Running Detection Agent...")
        detections = detection_agent.run(calibrated_pixel_data, calibrated_header)
        pipeline_run_results['detections'] = detections
        logger.info(f"Detection Agent completed. Found {len(detections)} potential objects.")
        if detections:
            for i, det in enumerate(detections):
                logger.info(f"  Detection {i+1}: X={det['x']}, Y={det['y']}, Confidence={det['confidence']:.2f}")

        logger.info("Step 4: Running Orbit Agent...")
        orbital_elements = orbit_agent.run(detections, calibrated_header)
        pipeline_run_results['orbital_elements'] = orbital_elements
        logger.info(f"Orbit Agent completed. Estimated orbits for {len(orbital_elements)} objects.")
        if orbital_elements:
            for i, orbit in enumerate(orbital_elements):
                logger.info(f"  Orbit {i+1}: RA={orbit.get('ra', 'N/A')}, Dec={orbit.get('dec', 'N/A')}, Epoch={orbit.get('epoch', 'N/A')}")

        pipeline_run_results["status"] = "success"
        logger.info("Asteroid detection pipeline completed successfully.")
        
        # Update the global latest results
        latest_pipeline_results = pipeline_run_results
        return pipeline_run_results

    except FileNotFoundError:
        logger.error(f"Error: FITS file not found at {fits_file_path}. Please check the path.")
        pipeline_run_results["status"] = "failed"
        pipeline_run_results["error"] = "File not found"
        latest_pipeline_results = pipeline_run_results
        return pipeline_run_results
    except Exception as e:
        logger.critical(f"An unhandled error occurred during pipeline execution: {e}", exc_info=True)
        pipeline_run_results["status"] = "failed"
        pipeline_run_results["error"] = str(e)
        latest_pipeline_results = pipeline_run_results
        return pipeline_run_results
    finally:
        await asyncio.sleep(0.1)
        try:
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
                logger.info(f"Cleaned up dummy FITS file: {file_to_delete}")
            else:
                logger.debug(f"Dummy FITS file {file_to_delete} already removed or never existed.")
        except OSError as e:
            logger.warning(f"Error removing dummy FITS file {file_to_delete}: {e}")

async def simulate_data_stream(interval_seconds: int = 5):
    """
    Simulates a continuous stream of new FITS data and processes it.
    """
    observation_count = 0
    while True:
        observation_count += 1
        dummy_file_name = f"dummy_asteroid_image_{observation_count:04d}.fits"
        dummy_file_path = os.path.join(DUMMY_FITS_DIR, dummy_file_name)
        
        try:
            created_file = create_dummy_fits_file(dummy_file_path, observation_count)
            await run_asteroid_detection_pipeline_async(created_file)
        except Exception as e:
            logger.error(f"Error in data stream simulation loop: {e}", exc_info=True)
        
        await asyncio.sleep(interval_seconds)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting background data stream simulation...")
    asyncio.create_task(simulate_data_stream(interval_seconds=5))

@app.get("/latest_results")
async def get_latest_results():
    return latest_pipeline_results

@app.get("/")
async def get_root():
    return HTMLResponse("<h1>Asteroid Detection Pipeline Backend Running</h1><p>Poll /latest_results for updates.</p>")

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

