def select_model(task, candidates, preferred=None):
    """Select a registered candidate by task support and optional preference."""
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task cannot be empty.")
    eligible = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        tasks = candidate.get("tasks", [])
        if task in tasks and candidate.get("available", True):
            eligible.append(candidate)
    if preferred:
        for candidate in eligible:
            if candidate.get("name") == preferred:
                return candidate
    if not eligible:
        raise LookupError(f"No available model supports task {task!r}.")
    return sorted(eligible, key=lambda item: (
        float(item.get("priority", 100)),
        str(item.get("name", "")),
    ))[0]
