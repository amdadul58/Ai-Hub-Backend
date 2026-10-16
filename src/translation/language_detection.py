def detect_language_script(text):
    """Heuristic script detection, not a full language-identification model."""
    if not isinstance(text, str) or not text.strip():
        return {"language": "unknown", "confidence": 0.0, "method": "script_heuristic"}
    counts = {"arabic": 0, "bengali": 0, "cyrillic": 0, "latin": 0}
    for char in text:
        code = ord(char)
        if 0x0600 <= code <= 0x06FF:
            counts["arabic"] += 1
        elif 0x0980 <= code <= 0x09FF:
            counts["bengali"] += 1
        elif 0x0400 <= code <= 0x04FF:
            counts["cyrillic"] += 1
        elif char.isascii() and char.isalpha():
            counts["latin"] += 1
    total = sum(counts.values())
    if total == 0:
        return {"language": "unknown", "confidence": 0.0, "method": "script_heuristic"}
    script = max(counts, key=counts.get)
    labels = {"arabic": "ar", "bengali": "bn", "cyrillic": "ru", "latin": "en"}
    return {
        "language": labels[script],
        "confidence": counts[script] / total,
        "script": script,
        "method": "script_heuristic",
        "warning": "Script-based estimate; language may be different.",
    }
