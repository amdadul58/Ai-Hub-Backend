def analyze_frame(frame, detector, density_estimator=None):
    if not callable(detector):
        raise TypeError("detector must be callable.")
    detections = detector(frame)
    result = {"detections": detections, "vehicle_count": len(detections)}
    if density_estimator is not None:
        result["density"] = density_estimator(detections, frame)
    return result
