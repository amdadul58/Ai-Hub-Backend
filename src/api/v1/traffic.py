
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter(prefix="/traffic", tags=["Traffic Intelligence"])

detector = None

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


def get_detector():
    global detector
    if detector is None:
        try:
            from src.traffic_intelligence.vehicle_detection import VehicleDetector
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Traffic detection dependencies are unavailable."
            ) from exc
        detector = VehicleDetector()
    return detector


@router.get("/status")
def traffic_status():
    return {
        "module": "Saudi Traffic Intelligence AI",
        "status": "ready_for_video_upload",
        "input_type": "recorded_video",
        "supported_formats": sorted(VIDEO_EXTENSIONS),
        "max_upload_mb": 100,
    }


@router.post("/detect")
async def detect_vehicles(file: UploadFile = File(...)):
    try:
        import cv2
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="OpenCV is required for video detection."
        ) from exc
    extension = Path(file.filename or "").suffix.lower()

    if extension not in VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Upload an MP4, AVI, MOV, or MKV video.",
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            suffix=extension, delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            size = 0

            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break

                size += len(chunk)
                if size > MAX_VIDEO_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds the 100 MB limit.",
                    )

                temp_file.write(chunk)

        ai = get_detector()
        capture = cv2.VideoCapture(str(temp_path))

        if not capture.isOpened():
            raise HTTPException(
                status_code=400,
                detail="Could not open the uploaded video.",
            )

        frame_count = 0
        total_detections = 0
        vehicle_types = {}

        try:
            while frame_count < 300:
                ok, frame = capture.read()
                if not ok:
                    break

                result = ai.detect(frame)
                frame_count += 1
                total_detections += result["vehicle_count"]

                for vehicle in result["vehicles"]:
                    name = vehicle["type"]
                    vehicle_types[name] = (
                        vehicle_types.get(name, 0) + 1
                    )
        finally:
            capture.release()

        if frame_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No readable video frames found.",
            )

        return {
            "filename": file.filename,
            "frames_analyzed": frame_count,
            "frames_limit": 300,
            "total_vehicle_detections": total_detections,
            "vehicle_detections_by_type": vehicle_types,
            "note": (
                "Counts are detections across sampled frames, "
                "not unique vehicles."
            ),
        }

    finally:
        await file.close()
        if temp_path and temp_path.exists():
            temp_path.unlink()
