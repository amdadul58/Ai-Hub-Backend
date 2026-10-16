def translate_chunks(text, translator, source_language, target_language, max_chars=1000):
    from src.translation.text_chunking import chunk_text
    chunks = chunk_text(text, max_chars)
    translated = []
    for index, chunk in enumerate(chunks):
        translated.append({
            "index": index,
            "source_text": chunk,
            "translated_text": translator(chunk, source_language, target_language),
        })
    return {"chunks": translated, "chunk_count": len(translated)}
