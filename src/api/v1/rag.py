from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.rag.pipeline import index_document, search_documents

router = APIRouter(prefix="/rag", tags=["RAG"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf"}

class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)

@router.post("/index")
async def index_uploaded_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Supported file types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / filename

    try:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Maximum upload size is 10 MB.")

        destination.write_bytes(content)
        result = index_document(str(destination))

        return {
            "status": "indexed",
            "filename": filename,
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Document indexing failed: {exc}",
        ) from exc
    finally:
        await file.close()

@router.post("/search")
def search_index(request: SearchRequest):
    try:
        results = search_documents(request.query, top_k=request.top_k)
        return {
            "query": request.query,
            "count": len(results) if isinstance(results, list) else None,
            "results": results,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document search failed: {exc}",
        ) from exc
