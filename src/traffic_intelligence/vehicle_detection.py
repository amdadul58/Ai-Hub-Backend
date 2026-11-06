
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

    # Existing vehicle detection - preserved
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
                    int(value)
                    for value in box.xyxy[0].tolist()
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

    # New vehicle tracking - ByteTrack
    def track(self, frame):
        results = self.model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=list(VEHICLE_CLASSES.keys()),
            conf=0.35,
            verbose=False,
        )

        tracked_vehicles = []
        result = results[0]

        if result.boxes is not None:
            boxes = result.boxes
            track_ids = boxes.id

            for index, box in enumerate(boxes):
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())

                x1, y1, x2, y2 = (
                    int(value)
                    for value in box.xyxy[0].tolist()
                )

                track_id = (
                    int(track_ids[index].item())
                    if track_ids is not None
                    else None
                )

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                tracked_vehicles.append({
                    "track_id": track_id,
                    "type": VEHICLE_CLASSES.get(
                        class_id, "unknown"
                    ),
                    "confidence": round(confidence, 3),
                    "bbox": [x1, y1, x2, y2],
                    "center": [center_x, center_y],
                })

        return {
            "vehicle_count": len(tracked_vehicles),
            "vehicles": tracked_vehicles,
            "annotated_frame": result.plot(),
        }
