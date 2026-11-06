
from pathlib import Path
from tempfile import NamedTemporaryFile
import base64
import logging
import time

from fastapi import APIRouter, File, HTTPException, UploadFile
from src.database.session import database_connection


router = APIRouter(prefix="/traffic", tags=["Traffic Intelligence"])

detector = None

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


logger = logging.getLogger(__name__)


def _record_traffic_usage(status: str, latency_ms: float):
    try:
        with database_connection() as connection:
            connection.execute(
                """
                INSERT INTO inference_logs
                    (model_name, status, latency_ms, details_json)
                VALUES (%s, %s, %s, %s)
                """,
                ("Traffic AI", status, latency_ms, "{}"),
            )
    except Exception:
        logger.exception("Could not record Traffic AI usage")




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




@router.post("/detect-image")
async def detect_vehicle_image(file: UploadFile = File(...)):
    started_at = time.perf_counter()

    try:
        import cv2
        import numpy as np

        extension = Path(file.filename or "").suffix.lower()
        if extension not in IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Upload a JPG, JPEG, PNG, or WEBP image.",
            )

        image_bytes = await file.read(MAX_VIDEO_SIZE + 1)
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Image is empty.")

        if len(image_bytes) > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Image exceeds the 100 MB limit.",
            )

        image = cv2.imdecode(
            np.frombuffer(image_bytes, dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Could not read the uploaded image.",
            )

        result = get_detector().detect(image)
        success, encoded_image = cv2.imencode(
            ".jpg", result["annotated_frame"]
        )
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Could not encode the annotated image.",
            )

        _record_traffic_usage(
            "success", (time.perf_counter() - started_at) * 1000
        )

        return {
            "filename": file.filename,
            "image_width": int(image.shape[1]),
            "image_height": int(image.shape[0]),
            "total_vehicle_detections": result["vehicle_count"],
            "vehicles": result["vehicles"],
            "annotated_image_base64": base64.b64encode(
                encoded_image.tobytes()
            ).decode("ascii"),
            "annotated_image_format": "jpeg",
        }

    except HTTPException:
        raise
    except Exception as exc:
        _record_traffic_usage(
            "error", (time.perf_counter() - started_at) * 1000
        )
        logger.exception("Traffic AI image detection failed")
        raise HTTPException(
            status_code=500,
            detail="Image vehicle detection failed.",
        ) from exc
    finally:
        await file.close()


@router.post("/detect")
async def detect_vehicles(file: UploadFile = File(...)):
    started_at = time.perf_counter()
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
        _record_traffic_usage(
            "success", (time.perf_counter() - started_at) * 1000
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

    except HTTPException:
        _record_traffic_usage(
            "error", (time.perf_counter() - started_at) * 1000
        )
        raise
    except Exception:
        _record_traffic_usage(
            "error", (time.perf_counter() - started_at) * 1000
        )
        logger.exception("Traffic AI video detection failed")
        raise
    finally:
        await file.close()
        if temp_path and temp_path.exists():
            temp_path.unlink()

# ---------------------------------------------------------
# Unified Traffic Intelligence API
# Supports image/video, vehicle detection and ANPR
# ---------------------------------------------------------

_anpr_service = None


def get_anpr_service():
    global _anpr_service

    if _anpr_service is None:
        try:
            from src.traffic_intelligence.anpr.anpr_service import (
                ANPRService,
            )
            _anpr_service = ANPRService()
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="ANPR dependencies are unavailable.",
            ) from exc

    return _anpr_service


@router.post("/analyze")
async def analyze_traffic(
    file: UploadFile = File(...),
    country: str = "auto",
):
    started_at = time.perf_counter()
    temp_path = None

    try:
        import cv2
        import numpy as np

        country = country.strip().lower()

        if country not in {"auto", "saudi", "bangladesh"}:
            raise HTTPException(
                status_code=400,
                detail="country must be auto, saudi, or bangladesh.",
            )

        extension = Path(file.filename or "").suffix.lower()

        if extension not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Upload a supported image or video file.",
            )

        # Read upload with size protection.
        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
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
                        detail="Upload exceeds the 100 MB limit.",
                    )

                temp_file.write(chunk)

        anpr = get_anpr_service()

        # IMAGE ANALYSIS
        if extension in IMAGE_EXTENSIONS:
            image = cv2.imread(str(temp_path))

            if image is None:
                raise HTTPException(
                    status_code=400,
                    detail="Could not read uploaded image.",
                )

            vehicle_result = get_detector().detect(image)
            plate_result = anpr.analyze(image, country=country)

            response = {
                "filename": file.filename,
                "input_type": "image",
                "country_requested": country,
                "image_width": int(image.shape[1]),
                "image_height": int(image.shape[0]),
                "vehicle_detection": {
                    "vehicle_count": vehicle_result["vehicle_count"],
                    "vehicles": vehicle_result["vehicles"],
                },
                "anpr": plate_result,
            }



        # VIDEO ANALYSIS
        else:
            capture = cv2.VideoCapture(str(temp_path))

            if not capture.isOpened():
                capture.release()
                raise HTTPException(
                    status_code=400,
                    detail="Could not open uploaded video.",
                )

            fps = capture.get(cv2.CAP_PROP_FPS)

            if not fps or fps <= 0:
                capture.release()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid video FPS.",
                )

            frame_count = 0
            total_detections = 0
            vehicle_types = {}
            plate_results = []

            # Store previous center and frame number per vehicle
            previous_positions = {}
            speed_records = {}
            tracked_ids = set()

            ai = get_detector()

            try:
                while frame_count < 300:
                    ok, frame = capture.read()

                    frame_count += 1

                    if frame_count % 2 != 0:
                        continue

                    if not ok:
                        break



                    vehicle_result = ai.track(frame)

                    total_detections += vehicle_result["vehicle_count"]

                    current_positions = {}

                    for vehicle in vehicle_result["vehicles"]:
                        name = vehicle["type"]

                        vehicle_types[name] = (
                            vehicle_types.get(name, 0) + 1
                        )

                        track_id = vehicle["track_id"]

                        if track_id is None:
                            continue

                        tracked_ids.add(track_id)

                        center = vehicle["center"]

                        current_positions[track_id] = (
                            center,
                            frame_count,
                        )

                        previous = previous_positions.get(track_id)

                        if previous is not None:
                            previous_center, previous_frame = previous

                            frame_difference = (
                                frame_count - previous_frame
                            )

                            if frame_difference > 0:
                                dx = center[0] - previous_center[0]
                                dy = center[1] - previous_center[1]

                                pixel_distance = (
                                    (dx ** 2 + dy ** 2) ** 0.5
                                )

                                elapsed_time = frame_difference / fps

                                pixel_speed = (
                                    pixel_distance / elapsed_time
                                )

                                speed_records.setdefault(
                                    track_id, []
                                ).append(pixel_speed)

                    previous_positions = current_positions

                    # Run ANPR once every 30 frames
                    if frame_count % 60 == 0:
                        plate_result = anpr.analyze(
                            frame,
                            country=country,
                        )

                        if (
                            plate_result.get("plate_detected")
                            or plate_result.get("recognized_text")
                        ):
                            plate_results.append({
                                "frame": frame_count,
                                "result": plate_result,
                            })

            finally:
                capture.release()

            if frame_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No readable video frames found.",
                )

            tracked_vehicles = []

            for track_id, speeds in speed_records.items():
                if speeds:
                    tracked_vehicles.append({
                        "track_id": track_id,
                        "average_pixel_speed_per_second": round(
                            sum(speeds) / len(speeds), 2
                        ),
                        "speed_unit": "pixels/second",
                    })

            response = {
                "filename": file.filename,
                "input_type": "video",
                "country_requested": country,
                "frames_analyzed": frame_count,
                "frames_limit": 300,
                "video_fps": round(fps, 2),

                "vehicle_detection": {
                    "total_frame_detections": total_detections,
                    "detections_by_type": vehicle_types,
                },

                "vehicle_tracking": {
                    "tracked_vehicle_count": len(tracked_ids),
                    "vehicles_with_speed_data": len(tracked_vehicles),
                    "vehicles": tracked_vehicles,
                },

                "anpr_results": plate_results,

                "speed_note": (
                    "Speed is estimated in pixels per second. "
                    "Real-world km/h requires camera calibration."
                ),

                "note": (
                    "Vehicle detections are frame-level counts, not "
                    "unique vehicle counts. Track IDs may change "
                    "during occlusion or tracking loss."
                ),
            }

        _record_traffic_usage(
            "success",
            (time.perf_counter() - started_at) * 1000,
        )

        return response

    except HTTPException:
        _record_traffic_usage(
            "error",
            (time.perf_counter() - started_at) * 1000,
        )
        raise

    except Exception as exc:
        _record_traffic_usage(
            "error",
            (time.perf_counter() - started_at) * 1000,
        )
        logger.exception("Unified Traffic Intelligence analysis failed")

        raise HTTPException(
            status_code=500,
            detail="Traffic analysis failed.",
        ) from exc

    finally:
        await file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink()

