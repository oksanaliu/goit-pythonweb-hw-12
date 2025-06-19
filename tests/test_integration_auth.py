import pytest
from sqlalchemy import update
from app.models.models import User
from app.database.db import get_db
from app.repository.users import get_user_by_email


@pytest.mark.asyncio
async def test_register_and_login(client, db_session):
    user = {"email": "int@ex.com", "password": "Secret123"}

    r = await client.post("/auth/register", json=user)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == user["email"]

    await db_session.execute(
        update(User).where(User.email == user["email"]).values(is_verified=True)
    )
    await db_session.commit()

    form = {"username": user["email"], "password": user["password"]}
    r2 = await client.post("/auth/login", data=form)
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}
    r3 = await client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["email"] == user["email"]

@pytest.mark.asyncio
async def test_users_me_unauthorized(client):
    r = await client.get("/users/me")
    assert r.status_code == 401