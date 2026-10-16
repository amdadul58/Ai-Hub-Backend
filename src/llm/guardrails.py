def validate_input(text, max_chars=12000):
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    text = text.strip()
    if not text:
        raise ValueError("Input cannot be empty")
    if len(text) > max_chars:
        raise ValueError(f"Input exceeds {max_chars} characters")
    return text
