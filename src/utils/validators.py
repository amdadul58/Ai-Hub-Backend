import re
from pathlib import Path


def is_valid_identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) is not None


def validate_filename(filename, allowed_extensions=None):
    """Validate a plain filename and optionally restrict its extension."""
    if not isinstance(filename, str) or not filename.strip():
        return False
    if filename in {".", ".."} or Path(filename).name != filename:
        return False
    if "/" in filename or "\\" in filename:
        return False
    if allowed_extensions:
        allowed = {ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                   for ext in allowed_extensions}
        return Path(filename).suffix.lower() in allowed
    return True
