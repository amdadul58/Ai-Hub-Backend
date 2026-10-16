from pathlib import Path


def get_image_dimensions(path):
    """Return (width, height) using Pillow, if installed."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Image dimension inspection requires Pillow.") from exc
    with Image.open(Path(path)) as image:
        return image.size


def validate_image_file(path, allowed_extensions=None):
    file_path = Path(path)
    allowed = allowed_extensions or {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    return file_path.is_file() and file_path.suffix.lower() in {
        ext.lower() for ext in allowed
    }
