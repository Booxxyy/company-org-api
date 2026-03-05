from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_department():
    payload = {"name": "Test Department X"}

    response = client.post("/departments/", json=payload)

    assert response.status_code in (201, 409)

    data = response.json()

    if response.status_code == 201:
        assert data["name"] == "Test Department X"
        assert data["parent_id"] is None
        assert "id" in data
        assert "created_at" in data
    else:
        assert "detail" in data or "name" in data
