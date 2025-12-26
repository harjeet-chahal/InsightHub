import pytest
from httpx import AsyncClient
from apps.api.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health") 
        # Note: We didn't explicitly create a /health endpoint in main.py, 
        # usually FastAPI has openapi at /docs. Let's check if we added one?
        # If not, let's test a known endpoint or /docs.
        # Or even better, let's test /api/v1/workspaces which should return empty list or 401 if auth (no auth yet).
        
        # Actually I should verify if I added a health endpoint. I haven't. 
        # I'll test /api/v1/workspaces
        response = await ac.get("/api/v1/workspaces")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_workspace():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/workspaces", json={"name": "Test Workspace"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workspace"
    assert "id" in data
