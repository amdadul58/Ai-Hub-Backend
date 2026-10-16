from fastapi.testclient import TestClient

from main import app


def test_health_endpoint_returns_success():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_deep_learning_status_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/deep-learning/status")

    assert response.status_code == 200
    body = response.json()

    assert body["module"] == "Deep Learning"
    assert isinstance(body["torch_available"], bool)
    assert isinstance(body["torchvision_available"], bool)


def test_traffic_status_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/traffic/status")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "ready_for_video_upload"
    assert body["input_type"] == "recorded_video"
    assert body["max_upload_mb"] == 100
    assert set(body["supported_formats"]) == {
        ".mp4", ".avi", ".mov", ".mkv"
    }