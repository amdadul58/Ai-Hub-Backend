from pathlib import Path


def ensure_directory(path):
    """Create a directory if needed and return its Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_file_size(path):
    return Path(path).stat().st_size


def is_file_with_extension(path, extensions):
    file_path = Path(path)
    allowed = {ext.lower() if ext.startswith(".") else f".{ext.lower()}"
               for ext in extensions}
    return file_path.is_file() and file_path.suffix.lower() in allowed
