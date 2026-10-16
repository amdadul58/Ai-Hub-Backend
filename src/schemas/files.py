from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    filename: str
    path: str
    size_bytes: int = Field(ge=0)


class FileInfoResponse(BaseModel):
    filename: str
    size_bytes: int = Field(ge=0)
    content_type: str | None = None
