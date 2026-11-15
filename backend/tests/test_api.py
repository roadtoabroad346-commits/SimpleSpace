from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "simplespace-api"


def test_archive_rejects_invalid_coordinates() -> None:
    response = client.post(
        "/archive/observations",
        json={"ra": 361, "dec": 0},
    )
    assert response.status_code == 422


def test_archive_rejects_invalid_declination() -> None:
    response = client.post(
        "/archive/observations",
        json={"ra": 10, "dec": -91},
    )
    assert response.status_code == 422
