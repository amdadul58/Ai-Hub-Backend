from src.api.v1.deep_learning import (
    deep_learning_capabilities,
    deep_learning_status,
)


def test_deep_learning_status_reports_framework_availability():
    result = deep_learning_status()

    assert result["module"] == "Deep Learning"
    assert isinstance(result["torch_available"], bool)
    assert isinstance(result["torchvision_available"], bool)

    if result["torch_available"]:
        assert result["status"] == "available"
    else:
        assert result["status"] == "framework_not_installed"


def test_deep_learning_capabilities_lists_supported_features():
    result = deep_learning_capabilities()

    assert "mlp" in result["architectures"]
    assert "cnn" in result["architectures"]
    assert "train_one_epoch" in result["training"]
    assert "predict_batch" in result["inference"]
    assert result["note"]