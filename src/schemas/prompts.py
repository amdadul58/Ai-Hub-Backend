from pydantic import BaseModel, Field


class PromptCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    template: str = Field(min_length=1, max_length=20000)
    description: str = Field(default="", max_length=2000)
    variables: list[str] = Field(default_factory=list)


class PromptRenderRequest(BaseModel):
    template: str = Field(min_length=1, max_length=20000)
    values: dict = Field(default_factory=dict)


class PromptRenderResponse(BaseModel):
    rendered_prompt: str
