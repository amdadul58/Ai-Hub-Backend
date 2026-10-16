from pathlib import Path


def load_image(path, mode="RGB"):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Image loading requires Pillow.") from exc
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(str(image_path))
    with Image.open(image_path) as image:
        return image.convert(mode).copy()


def image_metadata(path):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Image metadata requires Pillow.") from exc
    with Image.open(path) as image:
        return {"format": image.format, "width": image.width,
                "height": image.height, "mode": image.mode}
