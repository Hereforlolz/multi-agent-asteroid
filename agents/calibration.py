class CalibrationAgent:
    def run(self, img_data):
        print(f"[CalibrationAgent] Calibrating image {img_data['img_path']}")
        img_data["wcs"] = "dummy_wcs_solution"
        return img_data
