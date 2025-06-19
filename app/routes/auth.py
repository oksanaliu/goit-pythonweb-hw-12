from fastapi import (
    APIRouter, Body, Depends, HTTPException, status,
    BackgroundTasks, Request
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.conf.config import settings
from app.database.db import get_db
from app.schemas.schemas import UserCreate, UserResponse, TokenModel
from app.repository.users import (
    get_user_by_email, create_user,
    update_token, confirm_user
)
from app.services.auth import auth_service
from app.services.email import send_verification_email, send_reset_email

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: UserCreate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Реєстрація нового користувача.

    Перевіряє, чи існує користувач з вказаним email.
    Якщо ні — створює користувача, хешує пароль та надсилає лист із підтвердженням.
    У режимі тестування користувач автоматично верифікується.
    """
    existing = await get_user_by_email(payload.email, db)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")

    hashed = auth_service.hash_password(payload.password)
    user = await create_user(payload, hashed, db)

    token = auth_service.create_access_token({"sub": user.email})

    if settings.testing:
        user.is_verified = True
        await db.commit()
    else:
        background_tasks.add_task(send_verification_email, user.email, token)

    return user

@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Вхід користувача.

    Перевіряє, чи існує користувач з таким email, чи пароль правильний,
    і чи верифіковано email. Повертає access і refresh токени.
    """
    user = await get_user_by_email(form_data.username, db)

    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")

    access = auth_service.create_access_token({"sub": user.email})
    refresh = auth_service.create_refresh_token({"sub": user.email})

    await update_token(user, refresh, db)

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Підтвердження електронної пошти користувача.

    Отримує email з токена, перевіряє існування користувача,
    підтверджує обліковий запис.
    """
    email = auth_service.decode_token(token)
    user = await get_user_by_email(email, db)

    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token")

    await confirm_user(user, db)

    return {"msg": "Email successfully verified"}

@router.post("/reset-password-request", status_code=status.HTTP_200_OK)
async def reset_request(
    background_tasks: BackgroundTasks,
    email: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Запит на скидання пароля.

    Якщо email знайдено, надсилається лист із інструкціями щодо скидання пароля.
    """
    user = await get_user_by_email(email, db)

    if user:
        token = auth_service.create_access_token({"sub": user.email})
        background_tasks.add_task(send_reset_email, user.email, token)

    return {"msg": "If that email exists, instructions have been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Скидання пароля користувача.

    Отримує email із токена, знаходить користувача,
    хешує новий пароль та зберігає його.
    """
    email = auth_service.decode_token(token)
    user = await get_user_by_email(email, db)

    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token")

    user.hashed_password = auth_service.hash_password(new_password)
    await db.commit()

    return {"msg": "Password has been reset"}