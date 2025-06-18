from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.db import get_db
from app.services.auth import auth_service
from app.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    update_avatar as repo_update_avatar,
    update_user_data,
)
from app.services.cloudinary_service import upload_avatar
from app.schemas.schemas import UserResponse, UserUpdate, UserCreate

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse, summary="Отримати інформацію про поточного користувача")
@limiter.limit("5/minute")
async def me(
    request: Request,
    current_user=Depends(auth_service.get_current_user),
) -> UserResponse:
    return current_user

@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Створити нового користувача")
async def create_new_user(
    payload: UserCreate = Body(...),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    existing = await get_user_by_email(payload.email, db)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    hashed = auth_service.hash_password(payload.password)
    user = await create_user(payload, hashed, db)
    return user

@router.patch("/me/avatar", response_model=UserResponse, summary="Оновити аватар користувача")
async def patch_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> UserResponse:
    url = await upload_avatar(file)
    return await repo_update_avatar(current_user, url, db)

@router.patch("/me", response_model=UserResponse, summary="Оновити дані користувача (без аватара)")
async def patch_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> UserResponse:
    if body.avatar_url:
        return await repo_update_avatar(current_user, body.avatar_url, db)
    return await update_user_data(current_user, body, db)
