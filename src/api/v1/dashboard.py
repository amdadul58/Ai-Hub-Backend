from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def dashboard_summary():
    return {
        "app": "AI Hub",
        "modules": [
            "traffic",
            "vision",
            "speech",
            "translation",
            "multimodal",
            "rag",
            "llm",
            "agents",
            "automation",
        ],
        "status": "available",
        "note": "Module listing only; this is not a live metrics report.",
    }
