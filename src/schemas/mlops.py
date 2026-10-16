from pydantic import BaseModel, Field


class ExperimentLogRequest(BaseModel):
    experiment_name: str = Field(min_length=1, max_length=128)
    parameters: dict = Field(default_factory=dict)
    metrics: dict = Field(default_factory=dict)
    tags: dict = Field(default_factory=dict)


class DriftRequest(BaseModel):
    reference: list[float] = Field(min_length=1)
    current: list[float] = Field(min_length=1)
    relative_threshold: float = Field(default=0.2, ge=0)


class ModelRegistrationRequest(BaseModel):
    name: str = Field(pattern=r"^[A-Za-z0-9_-]+$")
    version: str = Field(pattern=r"^v[0-9]+\.[0-9]+\.[0-9]+$")
    artifact_path: str = Field(min_length=1)
    metrics: dict = Field(default_factory=dict)
    stage: str = "staging"
