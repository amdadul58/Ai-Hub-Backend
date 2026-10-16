def chunk_text(text, max_chars=500):
    if max_chars < 1:
        raise ValueError("max_chars must be positive.")
    words = text.split()
    chunks, current = [], ""
    for word in words:
        if len(word) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(word[i:i + max_chars] for i in range(0, len(word), max_chars))
            continue
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars:
            chunks.append(current)
            current = word
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def chunk_sequence(items, chunk_size):
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
