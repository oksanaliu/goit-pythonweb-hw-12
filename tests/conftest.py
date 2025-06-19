import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.main import app
from app.database.db import get_db, AsyncSessionLocal, engine, Base
from app.models.models import User
from app.services.auth import auth_service
from app.repository.users import create_user

@pytest.fixture(scope="function", autouse=True)
def override_db_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("TESTING", "True")

@pytest.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture
async def current_user(client: AsyncClient, db_session: AsyncSession):
    email = "testuser@example.com"
    password = "Secret123"
    hashed = auth_service.hash_password(password)
    user = await create_user(type("U", (), {"email": email, "password": password}), hashed, db_session)
    await db_session.execute(update(User).where(User.email == email).values(is_verified=True))
    await db_session.commit()

    login = await client.post("/auth/login", data={"username": email, "password": password})
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return user