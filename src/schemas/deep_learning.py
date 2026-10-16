from pydantic import BaseModel, Field


class DeepLearningStatus(BaseModel):
    module: str = "Deep Learning"
    torch_available: bool
    torchvision_available: bool


class TrainConfig(BaseModel):
    epochs: int = Field(default=1, ge=1, le=1000)
    learning_rate: float = Field(default=0.001, gt=0, le=1)
    batch_size: int = Field(default=16, ge=1, le=1024)
    device: str = Field(default="cpu", pattern=r"^(cpu|cuda)$")
