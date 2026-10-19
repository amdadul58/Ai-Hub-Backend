
import logging
import threading
from pathlib import Path

import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

router = APIRouter(prefix="/translation", tags=["Translation AI"])
logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

# Use the exact snapshots verified on this computer.
MODELS = {
    "bn-en": {
        "model_id": "Helsinki-NLP/opus-mt-bn-en",
        "snapshot": (
            "models--Helsinki-NLP--opus-mt-bn-en/snapshots/"
            "098d427088fba65d683639e91742c783cc7c1434"
        ),
    },
    "en-bn": {
        "model_id": "shhossain/opus-mt-en-to-bn",
        "snapshot": (
            "models--shhossain--opus-mt-en-to-bn/snapshots/"
            "c746a1500332b7964cbcd0b6f363b8ab2d8b1186"
        ),
    },
}

_translators = {}
_model_lock = threading.Lock()


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    direction: str = Field(default="bn-en")


def get_cached_snapshot(direction: str) -> Path | None:
    model_info = MODELS[direction]
    snapshot = CACHE_DIR / model_info["snapshot"]

    if not (snapshot / "config.json").is_file():
        return None

    has_weights = any(
        (snapshot / name).is_file()
        for name in (
            "model.safetensors",
            "pytorch_model.bin",
            "pytorch_model.safetensors",
        )
    )

    if not has_weights:
        return None

    return snapshot


def cached_model_exists(direction: str) -> bool:
    return get_cached_snapshot(direction) is not None


def get_translator(direction: str):
    if direction not in MODELS:
        raise HTTPException(
            status_code=400,
            detail="Use direction 'bn-en' or 'en-bn'.",
        )

    if direction in _translators:
        return _translators[direction]

    with _model_lock:
        if direction in _translators:
            return _translators[direction]

        model_id = MODELS[direction]["model_id"]
        snapshot = get_cached_snapshot(direction)

        if snapshot is None:
            raise HTTPException(
                status_code=503,
                detail=f"Required local model files are missing for {model_id}.",
            )

        try:
            logger.info("Loading %s from local snapshot %s", model_id, snapshot)

            tokenizer = AutoTokenizer.from_pretrained(
                str(snapshot),
                local_files_only=True,
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                str(snapshot),
                local_files_only=True,
            )
            model.to("cpu")
            model.eval()

            _translators[direction] = (tokenizer, model)
            logger.info("Loaded translation model: %s", model_id)

            return tokenizer, model

        except Exception as exc:
            logger.exception("Could not load translation model %s", model_id)
            raise HTTPException(
                status_code=503,
                detail=f"Could not load cached translation model {model_id}.",
            ) from exc


@router.get("/status")
def translation_status():
    cached = {
        direction: cached_model_exists(direction)
        for direction in MODELS
    }

    return {
        "module": "Translation AI",
        "status": "ready" if all(cached.values()) else "models_not_all_cached",
        "device": "cpu",
        "supported_directions": list(MODELS),
        "models_cached": cached,
        "models_loaded": {
            direction: direction in _translators
            for direction in MODELS
        },
        "download_enabled": False,
    }


@router.post("/translate")
def translate_text(request: TranslationRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    tokenizer, model = get_translator(request.direction)

    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.inference_mode():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=256,
                num_beams=4,
            )

        translated_text = tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True,
        )

        return {
            "module": "Translation AI",
            "direction": request.direction,
            "original_text": text,
            "translated_text": translated_text,
            "status": "translation_completed",
        }

    except Exception as exc:
        logger.exception("Translation inference failed: %s", request.direction)
        raise HTTPException(
            status_code=422,
            detail="Translation inference failed. Check backend terminal logs.",
        ) from exc
