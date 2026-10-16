from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.api.v1.users import current_user_id
from src.services.file_service import save_upload, safe_upload_path

router = APIRouter(prefix="/files", tags=["Files"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(current_user_id),
):
    original_name = Path(file.filename or "upload.bin").name
    if not original_name or original_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Maximum upload size is 10 MB.")
    stored_name = f"user_{user_id}_{uuid4().hex}_{original_name}"
    try:
        result = save_upload(stored_name, content, MAX_UPLOAD_BYTES)
        return {
            "filename": result["filename"],
            "size_bytes": result["size_bytes"],
            "message": "Upload successful.",
        }
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await file.close()


@router.get("/{filename}")
def download_file(
    filename: str,
    user_id: str = Depends(current_user_id),
):
    expected_prefix = f"user_{user_id}_"
    if not filename.startswith(expected_prefix):
        raise HTTPException(status_code=404, detail="File not found.")
    try:
        path = safe_upload_path(filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid filename.") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path, filename=path.name)
