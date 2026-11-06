import logging
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.database.session import database_connection
from src.llm.generation import TextGenerator
from src.llm.model_loader import load_local_model
from src.llm.local_inference import LocalInference
from src.llm.ollama_inference import OllamaCloudInference

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

_generator = None
_model_error = "Ollama Cloud is not configured."


def _record_inference(model_name: str, status: str, latency_ms: float):
    """Save inference usage without interrupting the actual AI request."""
    try:
        with database_connection() as db:
            db.execute(
                """
                INSERT INTO inference_logs
                    (model_name, status, latency_ms, details_json)
                VALUES (%s, %s, %s, '{}')
                """,
                (model_name, status, latency_ms),
            )
    except Exception:
        logger.exception("Failed to save inference analytics")


def _configure_default_provider():
    global _generator, _model_error
    try:
        _generator = TextGenerator(inference=OllamaCloudInference())
        _model_error = ""
    except Exception:
        logger.exception("Default Ollama Cloud provider initialization failed")
        _generator = None
        _model_error = "Ollama Cloud initialization failed. Check server logs."


_configure_default_provider()


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
        "provider": (
            getattr(_generator.inference, "provider", "unknown")
            if _generator is not None else None
        ),
        "model": (
            getattr(_generator.inference, "model_name", None)
            if _generator is not None else None
        ),
        "detail": (
            "Ollama Cloud is ready."
            if _generator is not None else _model_error
        ),
    }


@router.post("/load-local")
def load_model(request: ModelLoadRequest):
    global _generator, _model_error
    try:
        tokenizer, model = load_local_model(request.model_path)
        inference = LocalInference(
            model, tokenizer, max_new_tokens=request.max_new_tokens
        )
        _generator = TextGenerator(inference=inference)
        _model_error = ""
        return {
            "status": "loaded",
            "model_loaded": True,
            "provider": "local",
            "model_path": request.model_path,
            "max_new_tokens": request.max_new_tokens,
        }
    except Exception as exc:
        logger.exception("Local LLM model loading failed")
        _model_error = "Model loading failed. Check server logs for details."
        raise HTTPException(status_code=400, detail=_model_error) from exc


@router.post("/generate")
def generate_text(request: GenerateRequest):
    if _generator is None:
        raise HTTPException(
            status_code=503,
            detail=_model_error or "No LLM provider configured.",
        )

    inference = _generator.inference
    model_name = (
        getattr(inference, "model_name", None)
        or getattr(inference, "provider", None)
        or type(inference).__name__
    )

    start_time = time.perf_counter()

    try:
        output = _generator.generate(
            request.prompt,
            system_prompt=request.system_prompt,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000
        _record_inference(model_name, "success", latency_ms)

        return {"response": output}

    except (TypeError, ValueError) as exc:
        latency_ms = (time.perf_counter() - start_time) * 1000
        _record_inference(model_name, "error", latency_ms)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        latency_ms = (time.perf_counter() - start_time) * 1000
        _record_inference(model_name, "error", latency_ms)
        logger.exception("LLM text generation failed")
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed. Check server logs.",
        ) from exc
