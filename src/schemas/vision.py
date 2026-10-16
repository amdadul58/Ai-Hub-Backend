from pydantic import BaseModel, Field


class VisionPredictionResponse(BaseModel):
    task: str
    result: dict = Field(default_factory=dict)


class VisionModelStatusResponse(BaseModel):
    available: bool
    model_name: str | None = None
    message: str = ""
