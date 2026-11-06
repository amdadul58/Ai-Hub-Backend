import re


def split_text(text, chunk_size=500, overlap=80):
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")

    text = str(text or "").replace("\ufeff", "")
    text = re.sub(r"\s*={3,}\s*", "\n\n", text)
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)

        if end < length:
            boundary = text.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        next_start = max(start + 1, end - overlap)

        # Move the next start to a word boundary, if possible.
        if next_start > 0 and next_start < length:
            if text[next_start - 1] != " " and text[next_start] != " ":
                next_space = text.find(" ", next_start, end)
                if next_space != -1:
                    next_start = next_space + 1

        start = next_start

    return chunks
