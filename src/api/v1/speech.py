from pathlib import Path
import sys

from fastapi import APIRouter, File, HTTPException, UploadFile, Query

router = APIRouter(prefix="/speech", tags=["Speech AI"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "uploads" / "speech"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SPEECH_LAB_SITE_PACKAGES = Path(
    r"D:\Ai Eng 26.2\Speech AI Lab\venv\Lib\site-packages"
)

if SPEECH_LAB_SITE_PACKAGES.is_dir():
    site_packages = str(SPEECH_LAB_SITE_PACKAGES)
    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)

ALLOWED_AUDIO_FORMATS = {
    ".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"
}
MAX_FILE_SIZE = 25 * 1024 * 1024

_whisper_model = None


def get_whisper_model():
    global _whisper_model

    if _whisper_model is None:
        try:
            import whisper
        except ImportError as exc:
            raise HTTPException(
                status_code=500,
                detail="Whisper is unavailable in the Speech AI Lab environment.",
            ) from exc

        model_path = (
            Path(r"D:\Ai Eng 26.2\Speech AI Lab")
            / "models"
            / "tiny.pt"
        )

        try:
            if not model_path.is_file():
                raise HTTPException(
                    status_code=500,
                    detail=f"Whisper model not found: {model_path}",
                )

            _whisper_model = whisper.load_model(
                str(model_path),
                device="cpu",
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Could not load Whisper model: {exc}",
            ) from exc

    return _whisper_model


@router.get("/status")
def speech_status():
    return {
        "module": "Speech AI",
        "status": "ready_for_audio_upload_and_transcription",
        "whisper_environment_found": SPEECH_LAB_SITE_PACKAGES.is_dir(),
        "model": "Whisper Tiny",
        "device": "cpu",
        "default_language": "bn",
        "supported_formats": sorted(ALLOWED_AUDIO_FORMATS),
        "max_upload_mb": 25,
        "transcription_endpoint": "/api/v1/speech/transcribe",
    }


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format.",
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty.",
            )

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Maximum audio file size is 25 MB.",
            )

        filename = Path(file.filename or "audio").name
        output_path = UPLOAD_DIR / filename
        output_path.write_bytes(content)

        return {
            "module": "Speech AI",
            "filename": filename,
            "size_bytes": len(content),
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
        description="Language code, e.g. bn for Bengali or en for English.",
    ),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Use WAV, MP3, M4A, OGG, FLAC, or WEBM.",
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty.",
            )

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Maximum audio file size is 25 MB.",
            )

        filename = Path(file.filename or "audio").name
        audio_path = UPLOAD_DIR / filename
        audio_path.write_bytes(content)

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
                detail=f"Audio transcription failed: {exc}",
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