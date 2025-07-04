from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database.db import Base, engine
from app.routes.auth import router as auth_router
from app.routes.contacts import router as contacts_router
from app.routes.users import router as users_router

app = FastAPI(
    title="Contact Book API",
    description="Контактна книга з реєстрацією, JWT, верифікацією email, ролями та Redis-кешем",
    version="1.0.0",
)

limiter = Limiter(key_func=lambda request: request.client.host)
limiter.enabled = False 
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(users_router)

@app.on_event("startup")
async def on_startup():
    """
    Подія запуску FastAPI застосунку.

    Створює всі таблиці в базі даних, використовуючи SQLAlchemy metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)