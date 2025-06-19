import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.models import Contact, User
from app.database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

@pytest.mark.asyncio
async def test_read_contact_by_id(client, db_session, current_user):
    contact = Contact(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="123456789",
        birthday="2000-01-01",
        user_id=current_user.id,
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    response = await client.get(f"/contacts/{contact.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == contact.id

@pytest.mark.asyncio
async def test_read_contact_not_found(client):
    response = await client.get("/contacts/99999")  
    assert response.status_code == status.HTTP_404_NOT_FOUND
