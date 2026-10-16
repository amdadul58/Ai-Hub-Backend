import re
import unicodedata


def normalize_text(text):
    """Normalize Unicode and collapse repeated whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def truncate_text(text, max_chars, suffix="..."):
    if max_chars < 0:
        raise ValueError("max_chars must be non-negative.")
    if len(text) <= max_chars:
        return text
    if max_chars <= len(suffix):
        return suffix[:max_chars]
    return text[:max_chars - len(suffix)] + suffix
