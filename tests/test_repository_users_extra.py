import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirm_user,
    update_avatar,
)
from app.schemas.schemas import UserCreate

@pytest.mark.asyncio
async def test_update_token_and_refresh(db_session: AsyncSession):
    user_in = UserCreate(email="tokentest@ex.com", password="pwd")
    user = await create_user(user_in, db_session)
    await update_token(user, "my_refresh_token", db_session)
    fresh = await get_user_by_email("tokentest@ex.com", db_session)
    assert fresh.refresh_token == "my_refresh_token"

@pytest.mark.asyncio
async def test_confirm_user_sets_verified(db_session: AsyncSession):
    user_in = UserCreate(email="confirm@ex.com", password="pwd")
    user = await create_user(user_in, db_session)
    assert not user.is_verified
    user2 = await confirm_user(user, db_session)
    assert user2.is_verified

@pytest.mark.asyncio
async def test_update_avatar_changes_url(db_session: AsyncSession):
    user_in = UserCreate(email="avatar@ex.com", password="pwd")
    user = await create_user(user_in, db_session)
    assert user.avatar_url is None
    url = "https://example.com/avatar.png"
    user2 = await update_avatar(user, url, db_session)
    assert user2.avatar_url == url