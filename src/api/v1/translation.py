
from pathlib import Path

import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/translation", tags=["Translation AI"])

MODELS = {
    "bn-en": "Helsinki-NLP/opus-mt-bn-en",
    "en-bn": "shhossain/opus-mt-en-to-bn",
}

CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"
_translators = {}


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    direction: str = Field(default="bn-en")


def get_translator(direction: str):
    if direction not in MODELS:
        raise HTTPException(
            status_code=400,
            detail="Use direction 'bn-en' or 'en-bn'.",
        )

    if direction in _translators:
        return _translators[direction]

    model_id = MODELS[direction]
    cache_path = CACHE_DIR / (
        "models--" + model_id.replace("/", "--")
    )

    if not cache_path.is_dir():
        raise HTTPException(
            status_code=503,
            detail=f"Model is not cached locally: {model_id}",
        )

    try:

        from transformers import MarianTokenizer, AutoModelForSeq2SeqLM

        tokenizer = MarianTokenizer.from_pretrained(
            model_id,
            local_files_only=True,
        )

        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_id,
            local_files_only=True,
        )
        model.eval()

        _translators[direction] = (tokenizer, model)
        return tokenizer, model

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load cached model: {exc}",
        ) from exc


@router.get("/status")
def translation_status():
    return {
        "module": "Translation AI",
        "status": "ready",
        "device": "cpu",
        "supported_directions": ["bn-en", "en-bn"],
        "download_enabled": False,
    }


@router.post("/translate")
def translate_text(request: TranslationRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty.",
        )

    tokenizer, model = get_translator(request.direction)

    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=256,
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
        raise HTTPException(
            status_code=422,
            detail=f"Translation failed: {exc}",
        ) from exc
