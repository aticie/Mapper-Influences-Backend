import pytest

from app.test.helpers import add_fake_user_to_db


@pytest.mark.asyncio
async def test_get_user(test_client, headers, mongo_db, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)
    response = await test_client.get(f"users/{test_user_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_set_user_bio(test_client, headers, mongo_db, test_user_id):
    response = await test_client.post("users/bio", json={"bio": "test"}, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_and_remove_beatmap(test_client, headers, mongo_db, test_user_id):
    response = await test_client.post("users/add_beatmap", json={"id": 131891, "is_beatmapset": False}, headers=headers)
    assert response.status_code == 200
    response = await test_client.delete("users/remove_beatmap/diff/131891", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_influence_order(test_client, headers, mongo_db, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)
    body1 = {"beatmaps": [], "influenced_to": 418699,
             "type": 1, "description": "hi"}
    body2 = {"beatmaps": [], "influenced_to": 1848318,
             "type": 1, "description": "hi"}

    response = await test_client.post("influence", json=body1, headers=headers)
    assert response.status_code == 200
    response = await test_client.post("influence", json=body2, headers=headers)
    assert response.status_code == 200
    order_body = {"influence_ids": [1848318, 418699]}
    response = await test_client.post("users/influence-order", json=order_body, headers=headers)
    assert response.status_code == 200
    response = await test_client.get(f"influence/{test_user_id}", headers=headers)
    response = response.json()
    assert response[0]["influenced_to"] == 1848318
    assert response[1]["influenced_to"] == 418699
