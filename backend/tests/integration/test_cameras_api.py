"""Camera API integration tests (run against real Postgres via docker-compose)."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_create_camera():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/cameras",
            json={
                "name": "Test Camera",
                "code": "CAM-TEST-001",
                "location": {"type": "Point", "coordinates": [77.0, 12.0]},
                "status": "active",
                "is_simulated": True,
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "CAM-TEST-001"
    assert data["location"]["type"] == "Point"
    camera_id = data["id"]

    # Get camera
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get(f"/api/v1/cameras/{camera_id}")
    assert resp.status_code == 200

    # List cameras
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/cameras")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_camera_code_unique():
    transport = ASGITransport(app=app)
    payload = {
        "name": "Test Camera 2",
        "code": "CAM-UNIQUE",
        "location": {"type": "Point", "coordinates": [77.1, 12.1]},
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r1 = await ac.post("/api/v1/cameras", json=payload)
        r2 = await ac.post("/api/v1/cameras", json=payload)
    assert r1.status_code == 201
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_invalid_geojson_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/cameras",
            json={
                "name": "Bad Camera",
                "code": "CAM-BAD",
                "location": {"type": "Polygon", "coordinates": []},
            },
        )
    assert resp.status_code == 422