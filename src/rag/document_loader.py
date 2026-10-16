from pathlib import Path

def load_text(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")
    if path.suffix.lower() not in {".txt", ".md", ".csv", ".json"}:
        raise ValueError("Supported text formats: TXT, MD, CSV, JSON")
    return path.read_text(encoding="utf-8", errors="replace")
