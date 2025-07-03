class DetectionAgent:
    def run(self, calibrated_data):
        print(f"[DetectionAgent] Running detection on {calibrated_data['img_path']}")
        return [{"x": 100, "y": 150, "confidence": 0.95}]
