class OrbitAgent:
    def run(self, detections):
        print(f"[OrbitAgent] Estimating orbit from {len(detections)} detections")
        return {"a": 2.5, "e": 0.1, "i": 5.0}
