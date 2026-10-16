from pathlib import Path

def extract_text(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from src.rag.pdf_extractor import extract_pdf_text
        return extract_pdf_text(path)
    from src.rag.document_loader import load_text
    return load_text(path)
