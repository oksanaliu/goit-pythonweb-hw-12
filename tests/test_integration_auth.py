import pytest
from app.schemas.schemas import UserCreate

@pytest.mark.asyncio
async def test_register_and_login(client):
    user = {"email": "int@ex.com", "password": "Secret123"}
    r = await client.post("/auth/register", json=user)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == user["email"]

    form = {"username": user["email"], "password": user["password"]}
    r2 = await client.post("/auth/login", data=form)
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}
    r3 = await client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["email"] == user["email"]