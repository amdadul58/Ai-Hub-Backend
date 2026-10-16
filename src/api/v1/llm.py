from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.llm.generation import TextGenerator
from src.llm.model_loader import load_local_model
from src.llm.local_inference import LocalInference

router = APIRouter(prefix="/llm", tags=["LLM"])

_generator = None
_model_error = "No local model configured."


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    system_prompt: str | None = Field(default=None, max_length=4000)


class ModelLoadRequest(BaseModel):
    model_path: str = Field(min_length=1, max_length=1000)
    max_new_tokens: int = Field(default=128, ge=1, le=512)


@router.get("/status")
def llm_status():
    return {
        "status": "ready" if _generator is not None else "model_not_loaded",
        "model_loaded": _generator is not None,
        "detail": "Local inference status",
    }


@router.post("/load-local")
def load_model(request: ModelLoadRequest):
    global _generator, _model_error

    try:
        tokenizer, model = load_local_model(request.model_path)
        inference = LocalInference(
            tokenizer,
            model,
            max_new_tokens=request.max_new_tokens,
        )
        _generator = TextGenerator(inference=inference)
        _model_error = ""
        return {
            "status": "loaded",
            "model_path": request.model_path,
            "max_new_tokens": request.max_new_tokens,
        }
    except Exception as exc:
        _generator = None
        _model_error = str(exc)
        raise HTTPException(
            status_code=400,
            detail=f"Could not load local model: {exc}",
        ) from exc


@router.post("/generate")
def generate_text(request: GenerateRequest):
    if _generator is None:
        raise HTTPException(
            status_code=503,
            detail="No local model loaded. Load a compatible local model first.",
        )

    try:
        output = _generator.generate(
            request.prompt,
            system_prompt=request.system_prompt,
        )
        return {"response": output}
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Text generation failed: {exc}",
        ) from exc
