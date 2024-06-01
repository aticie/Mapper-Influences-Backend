import pytest

from app.test.helpers import add_fake_user_to_db


@pytest.mark.asyncio
async def test_leaderboard(test_client, mongo_db, headers, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)
    body = {"beatmaps": [], "influenced_to": 418699,
            "type": 1, "description": "hi"}
    response = await test_client.post("influence", json=body, headers=headers)
    assert response.status_code == 200
    response = await test_client.get("leaderboard?ranked=true&country=CN&limit=25&skip=0")
    assert response.status_code == 200
    response = response.json()
    assert len(response) >= 1
