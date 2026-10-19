from pathlib import Path
from functools import lru_cache
import io

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/multimodal", tags=["Multimodal AI"])

BASE_DIR = Path(__file__).resolve().parents[3]
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MODEL_ID = "Salesforce/blip-image-captioning-base"
CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"
CACHE_MODEL_DIR = CACHE_DIR / ("models--" + MODEL_ID.replace("/", "--"))


def cached_blip_exists():
    snapshots = CACHE_MODEL_DIR / "snapshots"
    return CACHE_MODEL_DIR.is_dir() and snapshots.is_dir() and any(
        (snapshot / "config.json").is_file()
        for snapshot in snapshots.iterdir()
        if snapshot.is_dir()
    )


@lru_cache(maxsize=1)
def load_captioner():
    if not cached_blip_exists():
        raise HTTPException(
            status_code=503,
            detail="BLIP model is not cached locally; no download was attempted.",
        )

    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration

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
            detail="Could not load the locally cached BLIP model.",
        ) from exc


@router.get("/status")
def multimodal_status():
    available = cached_blip_exists()
    return {
        "module": "Multimodal AI",
        "status": "ready" if available else "model_not_cached",
        "capabilities": ["image_captioning"],
        "model": MODEL_ID,
        "model_cached": available,
        "device": "cpu",
        "download_enabled": False,
    }


@router.post("/image-caption")
async def image_caption(file: UploadFile = File(...)):
    try:
        extension = Path(file.filename or "").suffix.lower()
        if file.content_type not in ALLOWED_TYPES and extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail="Upload a JPG, PNG, or WEBP image.",
            )

        content = await file.read(MAX_IMAGE_SIZE + 1)
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=413, detail="Image size must not exceed 10 MB.")

        try:
            from PIL import Image, UnidentifiedImageError

            with Image.open(io.BytesIO(content)) as source_image:
                source_image.verify()
            with Image.open(io.BytesIO(content)) as source_image:
                image = source_image.convert("RGB")
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Pillow is not installed in the active environment.",
            ) from exc
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid image.",
            ) from exc

        try:
            import torch
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="PyTorch is not installed in the active environment.",
            ) from exc

        processor, model = load_captioner()
        inputs = processor(images=image, return_tensors="pt")

        with torch.inference_mode():
            output_ids = model.generate(**inputs, max_new_tokens=60)

        caption = processor.decode(output_ids[0], skip_special_tokens=True).strip()
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
            detail="Image captioning failed.",
        ) from exc
    finally:
        await file.close()
