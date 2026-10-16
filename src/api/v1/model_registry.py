from fastapi import APIRouter

router = APIRouter(prefix="/model-registry", tags=["Model Registry"])


@router.get("/status")
def registry_status():
    return {
        "module": "Model Registry",
        "status": "available",
        "note": "Registry operations are available through src.mlops.model_registry.ModelRegistry.",
    }
