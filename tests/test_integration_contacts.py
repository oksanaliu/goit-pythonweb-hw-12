import pytest

@pytest.mark.asyncio
async def test_contacts_crud(client):
    payload = {"name": "Alice", "email": "alice@test.com", "phone": "+123"}
    r = await client.post("/contacts/", json=payload)
    assert r.status_code == 201
    contact = r.json()
    assert contact["name"] == "Alice"

    r2 = await client.get("/contacts/")
    assert r2.status_code == 200
    assert any(c["id"] == contact["id"] for c in r2.json())

    upd = {"name": "Alice Cooper"}
    r3 = await client.patch(f"/contacts/{contact['id']}", json=upd)
    assert r3.status_code == 200
    assert r3.json()["name"] == "Alice Cooper"

    r4 = await client.delete(f"/contacts/{contact['id']}")
    assert r4.status_code == 204