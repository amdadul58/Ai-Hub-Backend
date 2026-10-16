from pydantic import BaseModel, Field


class MultimodalTextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    context: list[str] = Field(default_factory=list, max_length=100)


class FusionRequest(BaseModel):
    scores: dict[str, float] = Field(min_length=1)
    weights: dict[str, float] | None = None
