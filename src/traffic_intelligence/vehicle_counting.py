def count_detections(detections, class_name=None):
    """Count detection records; expects dicts with optional class_name field."""
    items = list(detections)
    if class_name is not None:
        items = [item for item in items if item.get("class_name") == class_name]
    return {"count": len(items), "class_name": class_name}
