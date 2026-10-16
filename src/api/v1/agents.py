from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.workflow import AgentWorkflow
from src.agents.tool_registry import AgentToolRegistry
from src.agents.tool_executor import ToolExecutor
from src.agents.permissions import DEFAULT_ALLOWED_TOOLS
from src.rag.pipeline import search_documents

router = APIRouter(prefix="/agents", tags=["Agents"])

def summarize_text(text: str):
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    return {"summary": ". ".join(sentences[:3]) + ("." if sentences else ""), "method": "basic_extractive"}

def build_workflow():
    registry = AgentToolRegistry()
    registry.register("search_documents", search_documents)
    registry.register("summarize_text", summarize_text)
    executor = ToolExecutor(registry, allowed_tools=DEFAULT_ALLOWED_TOOLS)
    return AgentWorkflow(executor=executor)

class AgentRequest(BaseModel):
    task: str = Field(min_length=1, max_length=1000)
    query: str = Field(default="", max_length=2000)
    text: str = Field(default="", max_length=10000)
    top_k: int = Field(default=5, ge=1, le=20)

@router.get("/status")
def agent_status():
    return {"status": "available", "mode": "rule-based workflow"}

@router.post("/run")
def run_agent(request: AgentRequest):
    try:
        workflow = build_workflow()
        return workflow.run(
            request.task,
            query=request.query or request.task,
            top_k=request.top_k,
            text=request.text or request.task,
        )
    except (PermissionError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc
