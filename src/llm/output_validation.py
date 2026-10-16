def validate_output(text, max_chars=20000):
    if not isinstance(text, str):
        raise TypeError("Model output must be a string")
    text = text.strip()
    if not text:
        raise ValueError("Model returned an empty response")
    if len(text) > max_chars:
        text = text[:max_chars]
    return text
