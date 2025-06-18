from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.db import get_db
from app.models.models import Contact
from app.schemas.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    new_contact = Contact(**payload.dict(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> List[ContactResponse]:
    result = await db.execute(select(Contact).where(Contact.user_id == current_user.id))
    return result.scalars().all()

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> ContactResponse:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> ContactResponse:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    if payload.email:
        dup = await db.execute(
            select(Contact).where(
                Contact.email == payload.email,
                Contact.id != contact_id,
                Contact.user_id == current_user.id
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(contact, field, value)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> None:
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    await db.delete(contact)
    await db.commit()