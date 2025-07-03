# pipeline.py
import logging
import os
import numpy as np
from typing import Dict, Any, List, Tuple

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

# Define a placeholder for a FITS file path.
# In a real scenario, this would come from an ingestion queue or user input.
# For demonstration, we'll simulate a dummy FITS file creation.
DUMMY_FITS_FILE_PATH = "dummy_asteroid_image.fits"

def create_dummy_fits_file(file_path: str):
    """
    Creates a dummy FITS file for testing purposes.
    In a real system, this file would be ingested from a telescope.
    """
    from astropy.io import fits
    # Create dummy pixel data (e.g., a 100x100 array of random values)
    pixel_data = np.random.rand(100, 100).astype(np.float32) * 1000
    # Create a primary HDU
    hdu = fits.PrimaryHDU(pixel_data)
    # Create a header with some basic information
    hdu.header['DATE'] = '2025-07-03T12:00:00'
    hdu.header['EXPTIME'] = 30.0
    hdu.header['TELESCOP'] = 'DummyScope'
    hdu.header['OBSERVER'] = 'AI_Pipeline'
    # Write the HDU to a FITS file
    try:
        hdu.writeto(file_path, overwrite=True)
        logger.info(f"Dummy FITS file created at: {file_path}")
    except Exception as e:
        logger.error(f"Failed to create dummy FITS file: {e}")
        raise

def run_asteroid_detection_pipeline(fits_file_path: str) -> Dict[str, Any]:
    """
    Orchestrates the multi-agent asteroid detection pipeline.

    Args:
        fits_file_path (str): The path to the FITS image file to process.

    Returns:
        Dict[str, Any]: A dictionary containing the final processed results,
                        including detections and estimated orbital elements.
    """
    logger.info(f"Starting asteroid detection pipeline for {fits_file_path}")
    
    pipeline_results: Dict[str, Any] = {}

    try:
        # --- Initialize Agents ---
        ingest_agent = IngestAgent()
        calibration_agent = CalibrationAgent()
        detection_agent = DetectionAgent()
        orbit_agent = OrbitAgent()

        # --- Step 1: Ingest Image ---
        logger.info("Step 1: Running Ingest Agent...")
        pixel_data, header = ingest_agent.run(fits_file_path)
        pipeline_results['ingested_header'] = header.copy() # Store a copy of the header
        logger.info(f"Ingest Agent completed. Image dimensions: {pixel_data.shape}, Header keys: {len(header)}")

        # --- Step 2: Calibrate Image ---
        logger.info("Step 2: Running Calibration Agent...")
        calibrated_pixel_data, calibrated_header = calibration_agent.run(pixel_data, header)
        pipeline_results['calibrated_header'] = calibrated_header.copy() # Store a copy
        logger.info("Calibration Agent completed. Header updated with WCS info (fake).")

        # --- Step 3: Detect Asteroids ---
        logger.info("Step 3: Running Detection Agent...")
        detections = detection_agent.run(calibrated_pixel_data, calibrated_header)
        pipeline_results['detections'] = detections
        logger.info(f"Detection Agent completed. Found {len(detections)} potential objects.")
        if detections:
            for i, det in enumerate(detections):
                logger.info(f"  Detection {i+1}: X={det['x']}, Y={det['y']}, Confidence={det['confidence']:.2f}")

        # --- Step 4: Estimate Orbits ---
        logger.info("Step 4: Running Orbit Agent...")
        orbital_elements = orbit_agent.run(detections, calibrated_header)
        pipeline_results['orbital_elements'] = orbital_elements
        logger.info(f"Orbit Agent completed. Estimated orbits for {len(orbital_elements)} objects.")
        if orbital_elements:
            for i, orbit in enumerate(orbital_elements):
                logger.info(f"  Orbit {i+1}: RA={orbit.get('ra', 'N/A')}, Dec={orbit.get('dec', 'N/A')}, Epoch={orbit.get('epoch', 'N/A')}")

        logger.info("Asteroid detection pipeline completed successfully.")
        return pipeline_results

    except FileNotFoundError:
        logger.error(f"Error: FITS file not found at {fits_file_path}. Please check the path.")
        return {"status": "failed", "error": "File not found"}
    except Exception as e:
        logger.critical(f"An unhandled error occurred during pipeline execution: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    # Create a dummy FITS file for demonstration
    create_dummy_fits_file(DUMMY_FITS_FILE_PATH)

    # Run the pipeline
    final_results = run_asteroid_detection_pipeline(DUMMY_FITS_FILE_PATH)
    
    logger.info("\n--- Pipeline Final Results ---")
    logger.info(f"Pipeline Status: {final_results.get('status', 'success')}")
    if final_results.get('error'):
        logger.error(f"Pipeline Error: {final_results['error']}")
    
    if 'detections' in final_results:
        logger.info(f"Total Detections: {len(final_results['detections'])}")
    if 'orbital_elements' in final_results:
        logger.info(f"Total Orbital Elements Estimated: {len(final_results['orbital_elements'])}")

    # Clean up the dummy file
    try:
        os.remove(DUMMY_FITS_FILE_PATH)
        logger.info(f"Cleaned up dummy FITS file: {DUMMY_FITS_FILE_PATH}")
    except OSError as e:
        logger.warning(f"Error removing dummy FITS file: {e}")

