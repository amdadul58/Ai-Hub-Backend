
from pathlib import Path

from ultralytics import YOLO


MODEL_PATH = Path(
    r"D:\Ai Eng 26.2\Vision AI Lab\yolo11n.pt"
)

# COCO classes for common road vehicles
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class VehicleDetector:
    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.is_file():
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(str(model_path))

    def detect(self, frame):
        results = self.model.predict(
            source=frame,
            classes=list(VEHICLE_CLASSES.keys()),
            conf=0.35,
            verbose=False,
        )

        vehicles = []
        result = results[0]

        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())
                x1, y1, x2, y2 = (
                    int(value) for value in box.xyxy[0].tolist()
                )

                vehicles.append({
                    "type": VEHICLE_CLASSES.get(
                        class_id, "unknown"
                    ),
                    "confidence": round(confidence, 3),
                    "bbox": [x1, y1, x2, y2],
                })

        annotated_frame = result.plot()

        return {
            "vehicle_count": len(vehicles),
            "vehicles": vehicles,
            "annotated_frame": annotated_frame,
        }
