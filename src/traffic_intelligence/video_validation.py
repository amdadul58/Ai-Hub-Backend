from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}


def validate_video_path(path, allowed_extensions=None):
    video = Path(path)
    allowed = allowed_extensions or VIDEO_EXTENSIONS
    if not video.is_file():
        raise FileNotFoundError(str(video))
    if video.suffix.lower() not in allowed:
        raise ValueError(f"Unsupported video extension: {video.suffix}")
    return {"path": str(video.resolve()), "size_bytes": video.stat().st_size,
            "extension": video.suffix.lower()}
