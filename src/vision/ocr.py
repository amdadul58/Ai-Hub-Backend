def extract_text(image, ocr_engine):
    if not callable(ocr_engine):
        raise TypeError("ocr_engine must be callable.")
    result = ocr_engine(image)
    return {"task": "ocr", "text": result}
