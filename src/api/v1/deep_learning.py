from importlib.util import find_spec
from fastapi import APIRouter

router = APIRouter(prefix="/deep-learning", tags=["Deep Learning"])


@router.get("/status")
def deep_learning_status():
    """Report optional framework availability without loading model weights."""
    return {
        "module": "Deep Learning",
        "torch_available": find_spec("torch") is not None,
        "torchvision_available": find_spec("torchvision") is not None,
        "status": "available" if find_spec("torch") else "framework_not_installed",
    }


@router.get("/capabilities")
def deep_learning_capabilities():
    return {
        "architectures": ["mlp", "cnn", "resnet18_transfer_learning"],
        "training": ["train_one_epoch", "save_checkpoint"],
        "inference": ["predict_batch", "load_checkpoint"],
        "note": "Model training requires compatible PyTorch; pretrained ResNet weights may require a download.",
    }
