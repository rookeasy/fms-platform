from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_v1_placeholder_route() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/buildings")

    assert response.status_code == 200
    assert response.json()["status"] == "placeholder"


def test_standard_error_response() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/not-found")

    assert response.status_code == 404
    assert "error" in response.json()
    assert response.json()["error"]["code"] == "http_404"
