def detect_incident(detections, stopped_track_ids=None):
    stopped = set(stopped_track_ids or [])
    suspicious = [item for item in detections if item.get("track_id") in stopped]
    return {"incident_suspected": bool(suspicious),
            "matched_objects": suspicious,
            "note": "Heuristic result; verify before operational use."}
