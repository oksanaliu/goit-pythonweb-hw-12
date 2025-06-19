import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Contact, User
from app.main import app

@pytest.mark.asyncio
async def test_read_contact_by_id(client: AsyncClient, db_session: AsyncSession, current_user: User):
    contact = Contact(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="1234567890",
        birthday="1990-01-01",
        user_id=current_user.id,
    )
    db_session.add(contact)
    await db_session.commit()
    await db_session.refresh(contact)

    response = await client.get(f"/contacts/{contact.id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert response.json()["first_name"] == "Test"

@pytest.mark.asyncio
async def test_read_contact_not_found(client: AsyncClient, current_user: User):
    response = await client.get("/contacts/999999") 
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
