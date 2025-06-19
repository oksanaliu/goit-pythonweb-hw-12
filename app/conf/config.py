from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Клас для зчитування конфігураційних налаштувань з .env файлу.
    Містить всі необхідні параметри для роботи застосунку: база даних, пошта, Cloudinary, Redis тощо.
    """

    secret_key: str = Field(..., alias="SECRET_KEY", description="Секретний ключ для JWT токенів")
    algorithm: str = Field(..., alias="ALGORITHM", description="Алгоритм шифрування JWT")
    access_token_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES", description="Час дії access токена в хвилинах")
    refresh_token_expire_days: int = Field(..., alias="REFRESH_TOKEN_EXPIRE_DAYS", description="Час дії refresh токена в днях")

    database_url: str = Field(..., alias="DATABASE_URL", description="URL підключення до бази даних")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL", description="URL Redis сервера")

    mail_username: str = Field(..., alias="MAIL_USERNAME", description="Ім'я користувача для SMTP")
    mail_password: str = Field(..., alias="MAIL_PASSWORD", description="Пароль для SMTP")
    mail_from: str = Field(..., alias="MAIL_FROM", description="Email відправника")
    mail_port: int = Field(..., alias="MAIL_PORT", description="Порт поштового сервера")
    mail_server: str = Field(..., alias="MAIL_SERVER", description="Адреса поштового сервера")
    mail_from_name: str = Field("No-Reply", alias="MAIL_FROM_NAME", description="Ім'я відправника в листі")

    cloudinary_name: str = Field(..., alias="CLOUDINARY_NAME", description="Ім’я облікового запису Cloudinary")
    cloudinary_api_key: str = Field(..., alias="CLOUDINARY_API_KEY", description="API ключ Cloudinary")
    cloudinary_api_secret: str = Field(..., alias="CLOUDINARY_API_SECRET", description="Секрет Cloudinary")

    testing: bool = Field(False, alias="TESTING", description="Режим тестування, використовується для запуску SQLite")

    class Config:
        """
        Налаштування для зчитування змінних середовища з файлу .env.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        allow_population_by_field_name = True


settings = Settings()

if settings.testing:
    settings.database_url = "sqlite+aiosqlite:///:memory:"