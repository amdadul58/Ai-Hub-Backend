from pathlib import Path
from uuid import uuid4

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/vision", tags=["Vision AI"])

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "ai_models" / "yolo11n.pt"
UPLOAD_DIR = BASE_DIR / "uploads" / "vision"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
_model = None


def get_model():
    global _model

    if _model is not None:
        return _model

    if not MODEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Local YOLO model is not available.",
        )

    try:
        from ultralytics import YOLO
        _model = YOLO(str(MODEL_PATH))
        return _model
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ultralytics is not installed in the active environment.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load the local YOLO model.",
        ) from exc


@router.get("/status")
def vision_status():
    return {
        "module": "Vision AI",
        "status": "ready" if MODEL_PATH.is_file() else "model_not_found",
        "model_exists": MODEL_PATH.is_file(),
        "model_path": str(MODEL_PATH),
        "supported_formats": sorted(ALLOWED_EXTENSIONS),
        "max_upload_mb": 10,
    }


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        extension = Path(file.filename or "").suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Use JPG, JPEG, PNG, or WEBP.",
            )

        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Maximum image size is 10 MB.")

        try:
            import cv2
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="OpenCV is not installed in the active environment.",
            ) from exc

        image = cv2.imdecode(
            np.frombuffer(content, dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        model = get_model()
        results = model.predict(source=image, conf=0.25, verbose=False)

        detections = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                detections.append({
                    "class_id": class_id,
                    "label": model.names[class_id],
                    "confidence": round(float(box.conf[0].item()), 4),
                    "box_xyxy": [
                        round(float(value), 2)
                        for value in box.xyxy[0].tolist()
                    ],
                })

        filename = f"{uuid4().hex}{extension}"
        output_path = UPLOAD_DIR / filename
        output_path.write_bytes(content)

        return {
            "module": "Vision AI",
            "filename": file.filename,
            "saved_as": str(output_path),
            "image_width": int(image.shape[1]),
            "image_height": int(image.shape[0]),
            "model": str(MODEL_PATH),
            "status": "detection_completed",
            "total_detections": len(detections),
            "detections": detections,
        }
    finally:
        await file.close()
