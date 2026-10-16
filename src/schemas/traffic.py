from pydantic import BaseModel, Field


class TrafficAnalysisRequest(BaseModel):
    video_path: str = Field(min_length=1, max_length=2000)
    frame_interval: int = Field(default=30, ge=1, le=10000)
    max_frames: int = Field(default=100, ge=1, le=10000)


class TrafficAnalysisResponse(BaseModel):
    status: str
    vehicle_count: int = Field(default=0, ge=0)
    events: list[dict] = Field(default_factory=list)
