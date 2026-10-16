def weighted_score_fusion(scores, weights=None):
    """Combine numeric modality scores using non-negative weights."""
    if not scores:
        raise ValueError("scores cannot be empty.")
    values = {str(k): float(v) for k, v in scores.items()}
    if weights is None:
        weights = {key: 1.0 for key in values}
    if set(weights) != set(values):
        raise ValueError("weights must contain exactly the same keys as scores.")
    normalized_weights = {key: float(weights[key]) for key in values}
    if any(weight < 0 for weight in normalized_weights.values()):
        raise ValueError("weights must be non-negative.")
    total_weight = sum(normalized_weights.values())
    if total_weight <= 0:
        raise ValueError("At least one weight must be positive.")
    fused = sum(values[k] * normalized_weights[k] for k in values) / total_weight
    return {
        "fused_score": fused,
        "input_scores": values,
        "weights": normalized_weights,
        "method": "weighted_score_fusion",
    }


def concatenate_features(features):
    """Concatenate one-dimensional numeric feature sequences in key order."""
    if not features:
        raise ValueError("features cannot be empty.")
    result = []
    for name in sorted(features):
        values = features[name]
        if isinstance(values, (str, bytes)):
            raise TypeError(f"Feature {name!r} must be a numeric sequence.")
        result.extend(float(value) for value in values)
    return result
