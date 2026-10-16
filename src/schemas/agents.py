from pydantic import BaseModel, Field


class AgentTaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=10000)
    agent_name: str | None = Field(default=None, max_length=100)
    context: dict = Field(default_factory=dict)


class AgentTaskResponse(BaseModel):
    task_id: str
    status: str
    result: dict = Field(default_factory=dict)
