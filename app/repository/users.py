from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional

from app.models.models import User
from app.schemas.schemas import UserCreate, UserUpdate

async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Отримати користувача за email.

    :param email: Email користувача.
    :param db: Сесія бази даних.
    :return: Об'єкт користувача або None.
    """
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()

async def create_user(body: UserCreate, hashed_password: str, db: AsyncSession) -> User:
    """
    Створити нового користувача.

    :param body: Дані нового користувача (email, password).
    :param hashed_password: Хеш пароля.
    :param db: Сесія бази даних.
    :return: Створений об'єкт User.
    :raises HTTPException: Якщо email вже існує.
    """
    u = User(email=body.email, hashed_password=hashed_password)
    db.add(u)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    await db.refresh(u)
    return u

async def update_token(user: User, token: Optional[str], db: AsyncSession) -> None:
    """
    Оновити refresh token користувача.

    :param user: Об'єкт користувача.
    :param token: Новий refresh токен.
    :param db: Сесія бази даних.
    """
    user.refresh_token = token
    await db.commit()

async def confirm_user(user: User, db: AsyncSession) -> User:
    """
    Підтвердити email користувача (is_verified=True).

    :param user: Об'єкт користувача.
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт User.
    """
    user.is_verified = True
    await db.commit()
    await db.refresh(user)
    return user

async def update_avatar(user: User, url: str, db: AsyncSession) -> User:
    """
    Оновити аватар користувача.

    :param user: Об'єкт користувача.
    :param url: URL нового аватара.
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт User.
    """
    user.avatar_url = url
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_data(user: User, body: UserUpdate, db: AsyncSession) -> User:
    """
    Оновити дані користувача (email, пароль, аватар).

    :param user: Об'єкт користувача.
    :param body: Дані для оновлення.
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт User.
    """
    for field, value in body.dict(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user