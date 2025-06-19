import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db, init_db, AsyncSessionLocal

@pytest.mark.asyncio
async def test_init_db_runs_without_error():
    await init_db()

@pytest.mark.asyncio
async def test_get_db_returns_session():
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    await session.close()