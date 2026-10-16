from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    status: str
    message: str | None = None


class ErrorResponse(BaseModel):
    detail: str


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
