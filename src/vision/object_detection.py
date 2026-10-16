def detect_objects(image, detector):
    if not callable(detector):
        raise TypeError("detector must be callable.")
    result = detector(image)
    return {"task": "object_detection", "detections": result}
