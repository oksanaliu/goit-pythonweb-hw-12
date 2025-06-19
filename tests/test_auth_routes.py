import pytest
from httpx import AsyncClient
from sqlalchemy import update
from app.models.models import User

@pytest.mark.asyncio
async def test_register_email_exists(client, db_session):
    user_data = {"email": "test@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"

@pytest.mark.asyncio
async def test_login_unverified(client, db_session):
    user_data = {"email": "unverified@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)
    form_data = {"username": user_data["email"], "password": user_data["password"]}
    response = await client.post("/auth/login", data=form_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not verified"

@pytest.mark.asyncio
async def test_login_invalid_password(client, db_session):
    user_data = {"email": "wrongpass@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)
    await db_session.execute(
        update(User).where(User.email == user_data["email"]).values(is_verified=True)
    )
    await db_session.commit()
    form_data = {"username": user_data["email"], "password": "WrongPass"}
    response = await client.post("/auth/login", data=form_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_reset_password_request(client, db_session):
    user_data = {"email": "resetme@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)
    response = await client.post("/auth/reset-password-request", json={"email": user_data["email"]})
    assert response.status_code == 200
    assert "instructions" in response.json()["msg"]

@pytest.mark.asyncio
async def test_reset_password(client, db_session):
    user_data = {"email": "changeme@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)

    await db_session.execute(
        update(User).where(User.email == user_data["email"]).values(is_verified=True)
    )
    await db_session.commit()

    from app.services.auth import auth_service
    token = auth_service.create_access_token({"sub": user_data["email"]})

    response = await client.post("/auth/reset-password", json={
        "token": token,
        "new_password": "NewPass123"
    })

    assert response.status_code == 200
    assert response.json()["msg"] == "Password has been reset"

@pytest.mark.asyncio
async def test_verify_email(client, db_session):
    user_data = {"email": "verifyme@example.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)

    from app.services.auth import auth_service
    token = auth_service.create_access_token({"sub": user_data["email"]})

    response = await client.get(f"/auth/verify?token={token}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Email successfully verified"