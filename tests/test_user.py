import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.main import app
from app.database.db import get_db, AsyncSessionLocal
from app.models.models import User
from app.repository.users import create_user
from app.services.auth import auth_service

@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def test_user(db_session: AsyncSession):
    email = "contactuser@example.com"
    password = "Secret123"
    hashed = auth_service.hash_password(password)
    user = await create_user(type("U", (), {"email": email, "password": password}), hashed, db_session)
    await db_session.execute(
        update(User).where(User.email == email).values(is_verified=True)
    )
    await db_session.commit()
    return user

@pytest.fixture
async def authorized_client(test_user, db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        login = await client.post("/auth/login", data={"username": test_user.email, "password": "Secret123"})
        token = login.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

@pytest.mark.asyncio
async def test_create_contact(authorized_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+380501234567",
        "birthday": "1990-01-01",
        "additional_info": "Test contact"
    }
    response = await authorized_client.post("/contacts", json=data)
    assert response.status_code == 201
    assert response.json()["email"] == data["email"]

@pytest.mark.asyncio
async def test_get_contacts(authorized_client):
    response = await authorized_client.get("/contacts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_search_contacts(authorized_client):
    response = await authorized_client.get("/contacts/search?query=john")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_birthday_contacts(authorized_client):
    response = await authorized_client.get("/contacts/birthday")
    assert response.status_code == 200

