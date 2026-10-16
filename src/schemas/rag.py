from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    collection_name: str | None = Field(default=None, max_length=200)
    top_k: int = Field(default=5, ge=1, le=50)


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[dict] = Field(default_factory=list)
