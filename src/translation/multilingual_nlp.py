def normalize_multilingual_text(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    return " ".join(text.replace("\u200b", "").replace("\ufeff", "").split())


def analyze_text(text, language_detector=None):
    normalized = normalize_multilingual_text(text)
    detected = language_detector(normalized) if language_detector and normalized else None
    return {"text": normalized, "character_count": len(normalized),
            "word_count": len(normalized.split()), "language": detected}
