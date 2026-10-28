from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_salud():
    response = client.get("/salud")
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "ok"
