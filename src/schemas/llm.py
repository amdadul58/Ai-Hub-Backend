from pydantic import BaseModel, Field


class LLMGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    model_name: str | None = Field(default=None, max_length=200)
    max_new_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0, le=2)


class LLMGenerateResponse(BaseModel):
    text: str
    model_name: str | None = None
    usage: dict = Field(default_factory=dict)
