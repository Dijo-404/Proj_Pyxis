"""Smoke tests for the API application factory."""

from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_check() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Pyxis Compliance API"}
