import pytest

from app.test.helpers import add_fake_influence_to_db, add_fake_user_to_db


@pytest.mark.asyncio
async def test_add_and_delete_influence(test_client, mongo_db, headers, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)
    body1 = {"beatmaps": [], "influenced_to": 418699,
             "type": 1, "description": "hi"}
    response = await test_client.post("influence", json=body1, headers=headers)
    assert response.status_code == 200
    response = await test_client.delete("influence/418699", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_influence_and_mentions(test_client, mongo_db, headers, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)
    body1 = {"beatmaps": [], "influenced_to": 418699,
             "type": 1, "description": "hi"}
    response = await test_client.post("influence", json=body1, headers=headers)
    assert response.status_code == 200
    response = await test_client.get(f"influence/{test_user_id}", headers=headers)
    assert response.status_code == 200
    await add_fake_influence_to_db(mongo_db, 418699, test_user_id)
    response = await test_client.get(f"influence/{test_user_id}/mentions", headers=headers)
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 1
