from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

@router.get("/documents")
def list_documents():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    documents = [
        {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(UPLOAD_DIR.iterdir())
        if path.is_file()
    ]

    return {
        "count": len(documents),
        "documents": documents,
        "note": "Lists uploaded files; it does not verify vector indexing.",
    }
