from pathlib import Path

from fastapi import APIRouter
from src.llm.fine_tuning import check_fine_tuning_dependencies
from src.schemas.fine_tuning import FineTuningRequest

router = APIRouter(prefix="/fine-tuning", tags=["Fine-Tuning"])


@router.get("/status")
def fine_tuning_status():
    dependencies = check_fine_tuning_dependencies()
    return {
        "module": "LLM Fine-Tuning",
        "status": "available" if dependencies["available"] else "dependencies_missing",
        "dependencies": dependencies,
        "training_execution": "not_implemented",
    }


@router.get("/capabilities")
def fine_tuning_capabilities():
    return {
        "supported_configuration": [
            "model_name",
            "dataset_path",
            "epochs",
            "learning_rate",
            "batch_size",
        ],
        "training_execution": "not_implemented",
        "note": "This API currently checks configuration and dependencies; it does not start training.",
    }


@router.post("/validate")
def validate_fine_tuning_request(request: FineTuningRequest):
    dataset = Path(request.dataset_path).expanduser()

    if not dataset.is_file():
        return {
            "status": "invalid_dataset",
            "message": "Dataset path must point to an existing local file.",
            "dataset_exists": False,
        }

    dependencies = check_fine_tuning_dependencies()

    if not dependencies["available"]:
        return {
            "status": "dependencies_missing",
            "message": "Install the required optional packages before implementing training.",
            "dataset_exists": True,
            "dependencies": dependencies,
            "training_started": False,
        }

    return {
        "status": "validation_passed",
        "message": "Configuration and dependency checks passed. Training has not been implemented or started.",
        "dataset_exists": True,
        "dependencies": dependencies,
        "training_started": False,
    }
