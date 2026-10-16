def extract_image_text(path):
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "OCR requires pytesseract and Pillow; Tesseract OCR must also be installed."
        ) from exc
    with Image.open(path) as image:
        return pytesseract.image_to_string(image)
