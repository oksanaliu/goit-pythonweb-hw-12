"""
Модуль для надсилання електронних листів верифікації та скидання пароля.

Використовує FastMail з бібліотеки fastapi-mail.
"""

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


async def send_verification_email(email: EmailStr, token: str):
    """
    Надсилає лист для підтвердження електронної пошти.

    :param email: Email користувача
    :param token: Токен для підтвердження
    """
    link = f"http://localhost:8000/auth/verify?token={token}"
    message = MessageSchema(
        subject="Email verification",
        recipients=[email],
        body=f"Будь ласка, підтвердіть email за посиланням:\n{link}",
        subtype="plain"
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception:
        print(f"[DEV] Verification link: {link}")


async def send_reset_email(email: EmailStr, token: str):
    """
    Надсилає лист для скидання пароля.

    :param email: Email користувача
    :param token: Токен для скидання пароля
    """
    link = f"http://localhost:8000/auth/reset-password?token={token}"
    message = MessageSchema(
        subject="Password reset",
        recipients=[email],
        body=f"Щоб скинути пароль, перейдіть за посиланням:\n{link}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)