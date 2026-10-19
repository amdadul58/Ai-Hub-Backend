
import pytest
from fastapi.testclient import TestClient

from main import app
from src.api.v1 import deep_learning


@pytest.fixture
def client_and_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(deep_learning, "ARTIFACT_DIR", tmp_path)
    return TestClient(app)


def training_payload():
    return {
        "samples": [
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.1, 0.2],
            [0.2, 0.9],
            [0.9, 0.1],
            [0.8, 0.9],
        ],
        "targets": [0, 1, 1, 1, 0, 1, 1, 1],
        "epochs": 2,
        "learning_rate": 0.001,
    }


def test_training_api_creates_saved_model(client_and_artifacts):
    response = client_and_artifacts.post(
        "/api/v1/deep-learning/train",
        json=training_payload(),
    )

    assert response.status_code == 201
    result = response.json()
    assert result["architecture"] == "mlp"
    assert result["input_features"] == 2
    assert result["samples_trained"] == 8

    model_id = result["model_id"]
    checkpoint = deep_learning.ARTIFACT_DIR / f"{model_id}.pt"
    metadata = deep_learning.ARTIFACT_DIR / f"{model_id}.json"

    assert checkpoint.is_file()
    assert metadata.is_file()


def test_saved_model_prediction_api(client_and_artifacts):
    train_response = client_and_artifacts.post(
        "/api/v1/deep-learning/train",
        json=training_payload(),
    )
    assert train_response.status_code == 201

    model_id = train_response.json()["model_id"]

    response = client_and_artifacts.post(
        f"/api/v1/deep-learning/models/{model_id}/predict",
        json={"inputs": [[0.0, 0.0], [1.0, 1.0]]},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["model_id"] == model_id
    assert len(result["predictions"]) == 2

    for prediction in result["predictions"]:
        assert prediction["class"] in [0, 1]
        probabilities = prediction["probabilities"]
        assert set(probabilities) == {"0", "1"}
        assert sum(probabilities.values()) == pytest.approx(1.0, abs=1e-5)


def test_prediction_rejects_wrong_feature_count(client_and_artifacts):
    train_response = client_and_artifacts.post(
        "/api/v1/deep-learning/train",
        json=training_payload(),
    )
    assert train_response.status_code == 201

    model_id = train_response.json()["model_id"]

    response = client_and_artifacts.post(
        f"/api/v1/deep-learning/models/{model_id}/predict",
        json={"inputs": [[1.0, 2.0, 3.0]]},
    )

    assert response.status_code == 422


def test_prediction_returns_404_for_unknown_model(client_and_artifacts):
    response = client_and_artifacts.post(
        "/api/v1/deep-learning/models/"
        "00000000000000000000000000000000/predict",
        json={"inputs": [[0.0, 1.0]]},
    )

    assert response.status_code == 404


def test_model_metadata_api_returns_saved_metadata(client_and_artifacts):
    train_response = client_and_artifacts.post(
        "/api/v1/deep-learning/train",
        json=training_payload(),
    )
    assert train_response.status_code == 201

    model_id = train_response.json()["model_id"]

    response = client_and_artifacts.get(
        f"/api/v1/deep-learning/models/{model_id}"
    )

    assert response.status_code == 200
    assert response.json()["model_id"] == model_id
    assert response.json()["architecture"] == "mlp"
