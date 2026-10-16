from pydantic import BaseModel, Field


class SpeechTranscriptionResponse(BaseModel):
    text: str
    language: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)


class TextToSpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str | None = Field(default=None, max_length=20)
    voice: str | None = Field(default=None, max_length=100)
