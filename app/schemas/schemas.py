from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    """
    Базова схема контакту.

    :param first_name: Ім'я контакту.
    :param last_name: Прізвище контакту.
    :param email: Email контакту.
    :param phone: Телефон контакту.
    :param birthday: День народження.
    :param additional_info: Додаткова інформація (необов'язково).
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str]


class ContactCreate(ContactBase):
    """
    Схема створення нового контакту.
    """
    pass


class ContactUpdate(ContactBase):
    """
    Схема оновлення існуючого контакту.
    """
    pass


class ContactResponse(ContactBase):
    """
    Схема відповіді при читанні контакту з бази.

    :param id: Унікальний ідентифікатор контакту.
    :param user_id: ID користувача, якому належить контакт.
    """
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    """
    Схема реєстрації користувача.

    :param email: Email користувача.
    :param password: Пароль.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Схема відповіді з інформацією про користувача.

    :param id: ID користувача.
    :param email: Email користувача.
    :param is_verified: Статус верифікації.
    :param avatar_url: URL аватара (необов’язково).
    """
    id: int
    email: EmailStr
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """
    Схема оновлення профілю користувача.

    :param email: Новий email.
    :param password: Новий пароль.
    :param avatar_url: Новий URL аватара.
    """
    email: Optional[EmailStr]
    password: Optional[str]
    avatar_url: Optional[str]


class TokenModel(BaseModel):
    """
    Схема токенів доступу.

    :param access_token: JWT токен доступу.
    :param refresh_token: JWT токен оновлення.
    :param token_type: Тип токена (за замовчуванням "bearer").
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Дані з токена (payload).

    :param sub: Email користувача (sub).
    """
    sub: Optional[str] = None