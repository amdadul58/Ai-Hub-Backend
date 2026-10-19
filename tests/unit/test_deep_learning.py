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

def test_cnn_training_and_inference_cpu(tmp_path):
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from src.deep_learning.architectures.cnn import build_cnn
    from src.deep_learning.training.trainer import train_one_epoch, save_checkpoint
    from src.deep_learning.inference.predictor import predict_batch, load_checkpoint

    torch.manual_seed(42)
    model = build_cnn(num_classes=2)
    inputs = torch.randn(4, 3, 16, 16)
    targets = torch.tensor([0, 1, 0, 1])
    loader = DataLoader(TensorDataset(inputs, targets), batch_size=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    result = train_one_epoch(
        model, loader, optimizer, torch.nn.CrossEntropyLoss(), device="cpu"
    )
    assert result["samples"] == 4
    assert result["loss"] >= 0

    checkpoint_path = tmp_path / "model.pt"
    save_checkpoint(model, checkpoint_path, optimizer=optimizer, epoch=1)

    restored = build_cnn(num_classes=2)
    load_checkpoint(restored, checkpoint_path, device="cpu")
    predictions = predict_batch(restored, inputs, device="cpu")

    assert predictions.shape == (4, 2)
    assert predictions.device.type == "cpu"
    assert torch.isfinite(predictions).all()


def test_predict_batch_rejects_empty_batch():
    import pytest
    import torch
    from src.deep_learning.inference.predictor import predict_batch

    model = torch.nn.Linear(3, 2)
    with pytest.raises(ValueError):
        predict_batch(model, torch.empty(0, 3))


def test_predict_batch_rejects_non_tensor_input():
    import pytest
    import torch
    from src.deep_learning.inference.predictor import predict_batch

    with pytest.raises(TypeError):
        predict_batch(torch.nn.Linear(3, 2), [[1, 2, 3]])


def test_training_rejects_empty_loader():
    import pytest
    import torch
    from src.deep_learning.training.trainer import train_one_epoch

    model = torch.nn.Linear(3, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    with pytest.raises(ValueError, match="no batches"):
        train_one_epoch(
            model, [], optimizer, torch.nn.CrossEntropyLoss(), device="cpu"
        )


def test_load_checkpoint_rejects_missing_file():
    import pytest
    import torch
    from src.deep_learning.inference.predictor import load_checkpoint

    with pytest.raises(FileNotFoundError):
        load_checkpoint(torch.nn.Linear(3, 2), "missing_checkpoint_test.pt")
