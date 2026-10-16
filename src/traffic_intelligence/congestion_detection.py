def detect_congestion(vehicle_count, average_speed, count_threshold=20, speed_threshold=10):
    if vehicle_count < 0 or average_speed < 0:
        raise ValueError("Count and speed must be non-negative.")
    congested = vehicle_count >= count_threshold and average_speed <= speed_threshold
    return {"congested": congested, "vehicle_count": vehicle_count,
            "average_speed": average_speed}
