from fastapi import APIRouter
from src.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/status")
def health_status():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
