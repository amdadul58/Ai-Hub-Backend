from pathlib import Path
from uuid import uuid4
import sys

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

router = APIRouter(prefix="/speech", tags=["Speech AI"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "uploads" / "speech"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SPEECH_LAB_DIR = BASE_DIR.parent.parent / "Speech AI Lab"
SPEECH_LAB_SITE_PACKAGES = SPEECH_LAB_DIR / "venv" / "Lib" / "site-packages"
MODEL_CANDIDATES = [
    BASE_DIR / "ai_models" / "tiny.pt",
    BASE_DIR / "ai_models" / "speech" / "tiny.pt",
    SPEECH_LAB_DIR / "models" / "tiny.pt",
]

ALLOWED_AUDIO_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = 25 * 1024 * 1024
_whisper_model = None


def find_model_path():
    return next((path for path in MODEL_CANDIDATES if path.is_file()), None)


def get_whisper_model():
    global _whisper_model

    if _whisper_model is not None:
        return _whisper_model

    if find_model_path() is None:
        raise HTTPException(
            status_code=503,
            detail="Local Whisper Tiny model is not available.",
        )

    try:
        import whisper
    except ImportError:
        if SPEECH_LAB_SITE_PACKAGES.is_dir():
            path_string = str(SPEECH_LAB_SITE_PACKAGES)
            if path_string not in sys.path:
                sys.path.insert(0, path_string)
        try:
            import whisper
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Whisper is not installed in an available Python environment.",
            ) from exc

    try:
        _whisper_model = whisper.load_model(str(find_model_path()), device="cpu")
        return _whisper_model
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not load the local Whisper model.",
        ) from exc


@router.get("/status")
def speech_status():
    model_path = find_model_path()
    return {
        "module": "Speech AI",
        "status": "ready" if model_path else "model_not_found",
        "whisper_environment_found": SPEECH_LAB_SITE_PACKAGES.is_dir(),
        "model_exists": model_path is not None,
        "model_path": str(model_path) if model_path else None,
        "device": "cpu",
        "default_language": "bn",
        "supported_formats": sorted(ALLOWED_AUDIO_FORMATS),
        "max_upload_mb": 25,
        "transcription_endpoint": "/api/v1/speech/transcribe",
    }


async def read_audio_upload(file: UploadFile):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Use WAV, MP3, M4A, OGG, FLAC, or WEBM.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Maximum audio file size is 25 MB.")

    filename = f"{uuid4().hex}{extension}"
    output_path = UPLOAD_DIR / filename
    output_path.write_bytes(content)
    return filename, output_path, len(content)


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        filename, output_path, size_bytes = await read_audio_upload(file)
        return {
            "module": "Speech AI",
            "filename": filename,
            "size_bytes": size_bytes,
            "saved_as": str(output_path),
            "status": "audio_uploaded",
            "transcription_endpoint": "/api/v1/speech/transcribe",
        }
    finally:
        await file.close()


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Query(
        default="bn",
        min_length=2,
        max_length=10,
        description="Language code, e.g. bn for Bengali or en for English.",
    ),
):
    try:
        filename, audio_path, _ = await read_audio_upload(file)
        model = get_whisper_model()

        try:
            result = model.transcribe(
                str(audio_path),
                fp16=False,
                language=language,
                task="transcribe",
                temperature=0,
                condition_on_previous_text=False,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail="Audio transcription failed. Check the audio format and codec.",
            ) from exc

        text = result.get("text", "").strip()
        return {
            "module": "Speech AI",
            "filename": filename,
            "status": "transcription_completed" if text else "no_text_detected",
            "language": result.get("language"),
            "text": text,
            "model": "Whisper Tiny",
        }
    finally:
        await file.close()

