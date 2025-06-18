import pytest
from app.repository.users import get_user_by_email, create_user, update_token
from app.schemas.schemas import UserCreate

@pytest.mark.asyncio
async def test_create_and_get_user(db_session):
    user_in = UserCreate(email="test@ex.com", password="Password123")
    user = await create_user(user_in, db_session)
    assert user.id
    assert user.email == user_in.email

    fetched = await get_user_by_email(user.email, db_session)
    assert fetched.id == user.id
    assert fetched.email == user.email

@pytest.mark.asyncio
async def test_update_token(db_session):
    user_in = UserCreate(email="foo@bar.com", password="pass")
    user = await create_user(user_in, db_session)

    token = "some.jwt.token"
    await update_token(user, token, db_session)

    fetched = await get_user_by_email(user.email, db_session)
    assert fetched.refresh_token == token
