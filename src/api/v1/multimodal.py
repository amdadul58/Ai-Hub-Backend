
from pathlib import Path
from functools import lru_cache
import io

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(
    prefix="/multimodal",
    tags=["Multimodal AI"],
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

MODEL_ID = "Salesforce/blip-image-captioning-base"
CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"


@lru_cache(maxsize=1)
def load_captioner():
    """Load the cached BLIP model without downloading files."""
    try:
        import torch
        from transformers import (
            BlipProcessor,
            BlipForConditionalGeneration,
        )

        cached_model = CACHE_DIR / (
            "models--" + MODEL_ID.replace("/", "--")
        )

        if not cached_model.is_dir():
            raise RuntimeError(
                "BLIP model is not cached locally. "
                "No download was attempted."
            )

        processor = BlipProcessor.from_pretrained(
            MODEL_ID,
            local_files_only=True,
        )

        model = BlipForConditionalGeneration.from_pretrained(
            MODEL_ID,
            local_files_only=True,
        )

        model.to("cpu")
        model.eval()

        return processor, model

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Could not load local BLIP model: {exc}",
        ) from exc


@router.get("/status")
def multimodal_status():
    return {
        "module": "Multimodal AI",
        "status": "ready",
        "capabilities": ["image_captioning"],
        "device": "cpu",
        "download_enabled": False,
    }


@router.post("/image-caption")
async def image_caption(file: UploadFile = File(...)):
    try:
        import torch
        from PIL import Image, UnidentifiedImageError
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=415,
                detail="Upload a JPG, PNG, or WEBP image.",
            )

        content = await file.read(MAX_IMAGE_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Image size must not exceed 10 MB.",
            )

        try:
            with Image.open(io.BytesIO(content)) as source_image:
                source_image.verify()

            with Image.open(io.BytesIO(content)) as source_image:
                image = source_image.convert("RGB")

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as exc:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid image.",
            ) from exc

        processor, model = load_captioner()

        inputs = processor(
            images=image,
            return_tensors="pt",
        )

        with torch.inference_mode():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=60,
            )

        caption = processor.decode(
            output_ids[0],
            skip_special_tokens=True,
        ).strip()

        return {
            "module": "Multimodal AI",
            "filename": file.filename,
            "caption": caption,
            "status": "completed",
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image captioning failed: {exc}",
        ) from exc

    finally:
        await file.close()
