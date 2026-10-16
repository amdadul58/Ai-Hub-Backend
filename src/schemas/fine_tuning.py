from pydantic import BaseModel, Field


class FineTuningRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=200)
    dataset_path: str = Field(min_length=1, max_length=1000)
    epochs: int = Field(default=1, ge=1, le=100)
    learning_rate: float = Field(default=0.0001, gt=0, le=1)
    batch_size: int = Field(default=4, ge=1, le=1024)


class FineTuningJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
