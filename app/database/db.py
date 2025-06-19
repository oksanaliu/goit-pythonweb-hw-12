from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.conf.config import settings

if settings.testing:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.testing else {},
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

async def init_db() -> None:
    """
    Ініціалізує базу даних: створює всі таблиці, якщо вони ще не існують.
    Використовується при запуску FastAPI або в тестах.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    """
    Генерує асинхронну сесію бази даних.

    :yield: Сесія бази даних AsyncSession.
    """
    await init_db()
    async with AsyncSessionLocal() as session:
        yield session