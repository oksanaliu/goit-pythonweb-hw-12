from fastapi import Body, APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.db import get_db
from app.schemas.schemas import UserCreate, UserResponse, TokenModel
from app.repository.users import get_user_by_email, create_user, update_token, confirm_user
from app.services.auth import auth_service
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserCreate = Body(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await get_user_by_email(payload.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    hashed = auth_service.hash_password(payload.password)
    user = await create_user(payload, hashed, db)

    token = auth_service.create_access_token({"sub": user.email})
    if background_tasks:
        background_tasks.add_task(send_verification_email, user.email, token)

    return user

@router.post("/login", response_model=TokenModel)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(form_data.username, db)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")

    access = auth_service.create_access_token({"sub": user.email})
    refresh = auth_service.create_refresh_token({"sub": user.email})
    await update_token(user, refresh, db)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify(token: str, db: AsyncSession = Depends(get_db)):
    email = auth_service.decode_token(token)
    user = await get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    await confirm_user(user, db)
    return {"message": "Email successfully verified"}