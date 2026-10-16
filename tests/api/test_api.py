from main import app


def test_openapi_has_expected_api_routes():
    paths = app.openapi()["paths"]

    expected = [
        "/health",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/users/me",
        "/api/v1/history/conversations",
        "/api/v1/files/upload",
        "/api/v1/deep-learning/status",
        "/api/v1/mlops/status",
        "/api/v1/model-registry/status",
        "/api/v1/monitoring/status",
        "/api/v1/fine-tuning/status",
    ]

    missing = [path for path in expected if path not in paths]
    assert not missing, f"Missing API paths: {missing}"


def test_app_metadata():
    assert app.title == "AI Hub"
    assert app.version == "1.0.0"


def test_health_route_is_registered():
    paths = app.openapi()["paths"]
    assert "/health" in paths
    assert "get" in paths["/health"]
