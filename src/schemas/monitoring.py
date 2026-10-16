from pydantic import BaseModel, Field


class MonitoringEventRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=64)
    success: bool = True
    latency_ms: float | None = Field(default=None, ge=0)
    details: dict = Field(default_factory=dict)
