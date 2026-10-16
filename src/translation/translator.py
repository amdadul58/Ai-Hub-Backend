def translate_text(text, source_language, target_language, translator):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text cannot be empty.")
    if not source_language or not target_language:
        raise ValueError("Source and target language codes are required.")
    if source_language == target_language:
        return {"translated_text": text, "source_language": source_language,
                "target_language": target_language, "unchanged": True}
    if not callable(translator):
        raise TypeError("translator must be callable.")
    result = translator(text, source_language, target_language)
    return {"translated_text": result, "source_language": source_language,
            "target_language": target_language, "unchanged": False}
