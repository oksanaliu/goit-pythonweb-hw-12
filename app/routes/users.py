from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.schemas.schemas import UserResponse, UserUpdate
from app.repository.users import update_user_data, update_avatar
from app.services.cloudinary_service import upload_avatar
from app.services.auth import auth_service
from app.models.models import UserRole

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user=Depends(auth_service.get_current_user)):
    """
    Отримати дані поточного авторизованого користувача.

    :param current_user: Об'єкт користувача, витягнутий з токена.
    :return: Дані користувача.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    """
    Оновити профіль поточного користувача.

    :param body: Нові дані для оновлення.
    :param db: Сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Оновлений об'єкт користувача.
    """
    return await update_user_data(current_user, body, db)


def get_current_admin(user=Depends(auth_service.get_current_user)):
    """
    Перевірити, чи є користувач адміністратором.

    :param user: Поточний користувач.
    :raises HTTPException: Якщо роль не ADMIN.
    :return: Об'єкт користувача з роллю ADMIN.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Тільки адміністратори можуть виконувати цю операцію")
    return user


@router.patch(
    "/me/avatar",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin)]
)
async def change_avatar(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    """
    Оновити аватар поточного користувача (тільки для адміністратора).

    :param file: Завантажений файл зображення.
    :param db: Сесія бази даних.
    :param current_user: Поточний авторизований користувач.
    :return: Об'єкт користувача з оновленим URL аватару.
    """
    url = await upload_avatar(file)
    return await update_avatar(current_user, url, db)