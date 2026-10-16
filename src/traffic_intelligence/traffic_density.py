def estimate_density(vehicle_count, frame_area, low_threshold=0.02, high_threshold=0.08):
    if vehicle_count < 0 or frame_area <= 0:
        raise ValueError("vehicle_count must be non-negative and frame_area positive.")
    if not 0 <= low_threshold <= high_threshold:
        raise ValueError("Thresholds must satisfy 0 <= low <= high.")
    density = vehicle_count / frame_area
    level = "low" if density < low_threshold else "medium" if density < high_threshold else "high"
    return {"density": density, "level": level, "vehicle_count": vehicle_count}
