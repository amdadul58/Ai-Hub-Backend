from src.traffic_intelligence.video_validation import validate_video_path


def open_video(path):
    metadata = validate_video_path(path)
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Video processing requires OpenCV.") from exc
    capture = cv2.VideoCapture(metadata["path"])
    if not capture.isOpened():
        capture.release()
        raise ValueError("OpenCV could not open the video.")
    return capture
