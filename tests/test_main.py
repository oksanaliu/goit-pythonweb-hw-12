import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_invalid_login(client):
    response = await client.post("/auth/login", data={"username": "fake@test.com", "password": "wrongpass"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token_no_cookie(client):
    response = await client.get("/auth/refresh_token")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_unauthorized(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout_no_cookie(client):
    response = await client.post("/auth/logout")
    assert response.status_code == 401