from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.llm.prompt_manager import PromptManager

router = APIRouter(prefix="/prompts", tags=["Prompts"])
prompt_manager = PromptManager()

class PromptRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=10000)

@router.get("/")
def list_prompts():
    return {
        "prompts": [
            {"name": name, "prompt": prompt}
            for name, prompt in sorted(prompt_manager.prompts.items())
        ]
    }

@router.get("/{name}")
def get_prompt(name: str):
    try:
        return {"name": name, "prompt": prompt_manager.get(name)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.post("/register")
def register_prompt(request: PromptRequest):
    try:
        prompt_manager.register(request.name.strip(), request.prompt.strip())
        return {"status": "registered", "name": request.name.strip()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
