from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.vector_db.similarity_search import similarity_search

router = APIRouter(prefix="/vector-search", tags=["Vector Search"])

class VectorSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)

@router.post("/search")
def vector_search(request: VectorSearchRequest):
    try:
        results = similarity_search(request.query, top_k=request.top_k)
        return {
            "query": request.query,
            "count": len(results) if isinstance(results, list) else None,
            "results": results,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vector search failed: {exc}",
        ) from exc
