import json
import aioredis
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.config import settings
from app.database.db import get_db
from app.repository.users import get_user_by_email
from app.models.models import User

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

class AuthService:
    """
    Сервіс для автентифікації та авторизації користувачів.
    Забезпечує хешування паролів, створення та декодування токенів,
    а також отримання поточного користувача (з Redis або БД).
    """

    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Перевіряє, чи відповідає plain-текст пароля хешу.

        :param plain: Пароль у відкритому вигляді.
        :param hashed: Хешований пароль.
        :return: True, якщо паролі збігаються.
        """
        return pwd_ctx.verify(plain, hashed)

    def hash_password(self, pwd: str) -> str:
        """
        Хешує пароль.

        :param pwd: Пароль у відкритому вигляді.
        :return: Хеш пароля.
        """
        return pwd_ctx.hash(pwd)

    def create_access_token(self, data: dict) -> str:
        """
        Створює JWT access token.

        :param data: Дані (наприклад, email), які потрібно закодувати в токен.
        :return: Access token (JWT).
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        """
        Створює JWT refresh token.

        :param data: Дані для токена.
        :return: Refresh token (JWT).
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> Optional[str]:
        """
        Декодує токен і повертає email користувача (sub).

        :param token: JWT токен.
        :return: Email користувача або None, якщо токен недійсний.
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload.get("sub")
        except JWTError:
            return None

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """
        Отримує поточного користувача з токена.
        Використовує Redis як кеш для зменшення навантаження на базу даних.

        :param token: JWT токен доступу.
        :param db: Поточна сесія бази даних.
        :return: Об'єкт користувача.
        :raises HTTPException: Якщо токен недійсний або користувача не знайдено.
        """
        email = self.decode_token(token)
        if not email:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

        key = f"user:{email}"
        cached = await redis.get(key)
        if cached:
            data = json.loads(cached)
            user = User(**data)
        else:
            user = await get_user_by_email(email, db)
            if not user:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
            if not user.is_verified and not settings.testing:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
            await redis.set(
                key,
                json.dumps({
                    "id": user.id,
                    "email": user.email,
                    "is_verified": user.is_verified,
                    "avatar_url": user.avatar_url,
                    "refresh_token": user.refresh_token,
                    "role": user.role.value,
                }),
                ex=3600 
            )
        return user


auth_service = AuthService()