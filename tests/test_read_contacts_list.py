import pytest
from httpx import AsyncClient
from sqlalchemy import update
from app.models.models import User

@pytest.mark.asyncio
async def test_read_contacts_list(client: AsyncClient, db_session):
    user_data = {"email": "listuser@test.com", "password": "Secret123"}
    await client.post("/auth/register", json=user_data)
    await db_session.execute(
        update(User).where(User.email == user_data["email"]).values(is_verified=True)
    )
    await db_session.commit()

    form_data = {"username": user_data["email"], "password": user_data["password"]}
    response = await client.post("/auth/login", data=form_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    contact_data_1 = {
        "first_name": "Anna",
        "last_name": "Test",
        "email": "anna@example.com",
        "phone": "+123123123",
        "birthday": "1992-02-02",
        "extra_data": "extra"
    }
    contact_data_2 = {
        "first_name": "Mark",
        "last_name": "Test",
        "email": "mark@example.com",
        "phone": "+321321321",
        "birthday": "1989-03-03",
        "extra_data": "extra2"
    }
    await client.post("/contacts", json=contact_data_1, headers=headers)
    await client.post("/contacts", json=contact_data_2, headers=headers)

    list_response = await client.get("/contacts", headers=headers)
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)
    assert len(list_response.json()) == 2
