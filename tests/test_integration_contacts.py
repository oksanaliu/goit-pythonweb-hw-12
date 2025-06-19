import pytest
from sqlalchemy import update
from app.database.db import AsyncSessionLocal
from app.models.models import User

@pytest.mark.asyncio
async def test_contacts_crud(client):
    user = {"email": "alice@test.com", "password": "Secret123"}
    r = await client.post("/auth/register", json=user)
    assert r.status_code == 201

    async with AsyncSessionLocal() as session:
        await session.execute(update(User).where(User.email == user["email"]).values(is_verified=True))
        await session.commit()

    r2 = await client.post("/auth/login", data={"username": user["email"], "password": user["password"]})
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    contact_payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.contact@test.com",
        "phone": "+123456789",
        "birthday": "1995-05-20",
        "additional_info": "Test info"
    }
    r3 = await client.post("/contacts/", json=contact_payload, headers=headers)
    assert r3.status_code == 201
    contact_id = r3.json()["id"]

    r4 = await client.get("/contacts/", headers=headers)
    assert r4.status_code == 200
    contacts = r4.json()
    assert len(contacts) == 1
    assert contacts[0]["email"] == contact_payload["email"]

    r5 = await client.get(f"/contacts/{contact_id}", headers=headers)
    assert r5.status_code == 200
    assert r5.json()["first_name"] == "Alice"

    updated_data = {
        "first_name": "Alicia",
        "last_name": "Smith",
        "email": "alice.contact@test.com",
        "phone": "+123456789",
        "birthday": "1995-05-20",
        "additional_info": "Updated info"
    }
    r6 = await client.patch(f"/contacts/{contact_id}", json=updated_data, headers=headers)
    assert r6.status_code == 200
    assert r6.json()["first_name"] == "Alicia"

    r7 = await client.delete(f"/contacts/{contact_id}", headers=headers)
    assert r7.status_code == 204

    r8 = await client.get(f"/contacts/{contact_id}", headers=headers)
    assert r8.status_code == 404