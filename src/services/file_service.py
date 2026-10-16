import os
from pathlib import Path


def get_upload_directory():
    configured = os.getenv("AI_HUB_UPLOAD_DIR")
    if configured:
        directory = Path(configured).expanduser().resolve()
    else:
        directory = Path(__file__).resolve().parents[2] / "uploads"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_upload_path(filename):
    if not filename or filename in {".", ".."}:
        raise ValueError("Invalid filename.")
    if Path(filename).name != filename or "/" in filename or "\\" in filename:
        raise ValueError("Only a simple filename is allowed.")
    return get_upload_directory() / filename


def save_upload(filename, content, max_bytes=10 * 1024 * 1024):
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes.")
    if len(content) > max_bytes:
        raise ValueError("File exceeds the upload size limit.")
    destination = safe_upload_path(filename)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(destination)
    return {
        "filename": destination.name,
        "path": str(destination),
        "size_bytes": len(content),
    }
