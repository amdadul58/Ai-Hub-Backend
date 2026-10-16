def normalize_text(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    return " ".join(text.split())


def normalize_audio(samples, peak=1.0):
    """Normalize a numeric array or sequence without importing audio libraries."""
    if peak <= 0:
        raise ValueError("peak must be positive.")
    try:
        import numpy as np
        values = np.asarray(samples, dtype=np.float32)
        if values.size == 0:
            return values
        maximum = float(np.max(np.abs(values)))
        return values if maximum == 0 else values * (peak / maximum)
    except ImportError:
        values = [float(x) for x in samples]
        maximum = max((abs(x) for x in values), default=0.0)
        return values if maximum == 0 else [x * peak / maximum for x in values]
