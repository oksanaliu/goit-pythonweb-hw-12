from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.config import settings
from app.database.db import get_db
from app.repository.users import get_user_by_email
from app.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Сервіс для керування аутентифікацією, паролями та JWT токенами.
    """

    def __init__(self):
        """
        Ініціалізує налаштування JWT токенів з конфігурації.
        """
        self.secret_key: str = settings.secret_key
        self.algorithm: str = settings.algorithm
        self.access_token_expire_minutes: int = settings.access_token_expire_minutes
        self.refresh_token_expire_days: int = settings.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Перевіряє відповідність пароля хешу.

        :param plain_password: Звичайний (незахешований) пароль
        :param hashed_password: Хешований пароль
        :return: True, якщо пароль вірний
        """
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """
        Хешує пароль за допомогою bcrypt.

        :param password: Звичайний пароль
        :return: Хеш пароля
        """
        return pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        """
        Створює JWT access token з терміном дії в хвилинах.

        :param data: Дані, які будуть закодовані в токен (наприклад, {"sub": email})
        :return: Access token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        """
        Створює JWT refresh token з терміном дії в днях.

        :param data: Дані для токена
        :return: Refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[str]:
        """
        Декодує JWT токен та повертає email користувача (sub).

        :param token: JWT токен
        :return: Email або None, якщо токен недійсний
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except JWTError:
            return None

    async def get_current_user(
        self,
        token: str = Depends(),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """
        Повертає поточного користувача за токеном. Перевіряє верифікацію та існування.

        :param token: JWT токен
        :param db: Сесія бази даних
        :return: Об'єкт User
        :raises HTTPException: Якщо користувач не знайдений або не верифікований
        """
        email = self.decode_token(token)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )
        user = await get_user_by_email(email, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not user.is_verified and not settings.testing:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified",
            )
        return user


auth_service = AuthService()