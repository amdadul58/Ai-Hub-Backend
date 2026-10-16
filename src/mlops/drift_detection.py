def numeric_drift(reference, current, relative_threshold=0.2):
    """Compare numeric means; this is a simple alert heuristic, not a statistical test."""
    if relative_threshold < 0:
        raise ValueError("relative_threshold must be non-negative.")
    if not reference or not current:
        raise ValueError("Both reference and current data must be non-empty.")
    ref = [float(x) for x in reference]
    cur = [float(x) for x in current]
    if not all(map(_finite, ref + cur)):
        raise ValueError("Inputs must contain finite numbers.")
    ref_mean = sum(ref) / len(ref)
    cur_mean = sum(cur) / len(cur)
    scale = abs(ref_mean) or 1.0
    change = abs(cur_mean - ref_mean) / scale
    return {
        "reference_mean": ref_mean,
        "current_mean": cur_mean,
        "relative_change": change,
        "drift_detected": change > relative_threshold,
        "threshold": relative_threshold,
        "method": "relative difference between means",
    }


def _finite(value):
    import math
    return math.isfinite(value)
