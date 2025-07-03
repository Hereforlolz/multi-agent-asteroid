from agents.ingest import IngestAgent
from agents.calibration import CalibrationAgent
from agents.detection import DetectionAgent
from agents.orbit import OrbitAgent

def main():
    print("🚀 Starting Multi-Agent Asteroid Pipeline")
    img_path = "data/sample001.fits"
    img_data = IngestAgent().run(img_path)
    calibrated_data = CalibrationAgent().run(img_data)
    detections = DetectionAgent().run(calibrated_data)
    orbit = OrbitAgent().run(detections)
    print("\n✅ Pipeline Complete")
    print("Detections:", detections)
    print("Orbit Estimate:", orbit)

if __name__ == "__main__":
    main()
