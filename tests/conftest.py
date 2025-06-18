import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from dotenv import load_dotenv

from app.main import app
from app.database.db import get_db
from app.models.models import Base


# Завантаження змінних середовища з .env
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


# Створення тестового in-memory SQLite engine
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


# Підміна залежності get_db на тестову сесію
@pytest.fixture()
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


# Клієнт для тестування з підміною БД
@pytest.fixture()
async def client(override_get_db):
    app.dependency_overrides[get_db] = lambda: override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client