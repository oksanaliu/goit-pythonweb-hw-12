from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.db import Base


class UserRole(PyEnum):
    """
    Перелік можливих ролей користувача.
    - USER: звичайний користувач
    - ADMIN: адміністратор
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    Модель користувача.

    Атрибути:
        - id: Унікальний ідентифікатор
        - email: Адреса електронної пошти користувача
        - hashed_password: Хешований пароль
        - is_verified: Чи верифіковано email
        - avatar_url: URL аватара користувача
        - refresh_token: Refresh токен для оновлення доступу
        - role: Роль користувача (user або admin)
        - contacts: Список контактів, пов’язаних з користувачем
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    contacts = relationship("Contact", back_populates="owner", cascade="all, delete")


class Contact(Base):
    """
    Модель контакту.

    Атрибути:
        - id: Унікальний ідентифікатор
        - first_name: Ім’я контакту
        - last_name: Прізвище контакту
        - email: Email контакту
        - phone: Номер телефону
        - birthday: Дата народження
        - additional_info: Додаткова інформація
        - user_id: Зовнішній ключ до користувача
        - owner: Власник контакту (користувач)
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    birthday = Column(Date)
    additional_info = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="contacts")