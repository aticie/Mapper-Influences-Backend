import pytest
from httpx_ws import aconnect_ws

from app.test.helpers import add_fake_user_to_db


def assert_edit_bio(data, description):
    assert data["type"] == "EDIT_BIO"
    assert data["details"]["description"] == description
    assert data["details"]["beatmap"] == None
    assert data["details"]["influenced_to"] == None


def assert_add_beatmap(data, beatmap):
    assert data["type"] == "ADD_BEATMAP"
    assert data["details"]["description"] == None
    assert data["details"]["beatmap"] == beatmap
    assert data["details"]["influenced_to"] == None


def assert_add_influence(data, influenced_to):
    assert data["type"] == "ADD_INFLUENCE"
    assert data["details"]["description"] == "hi"
    assert data["details"]["beatmap"] == None
    assert data["details"]["influenced_to"] == influenced_to


# Sadly, can't test login in tests as it's a bit more complicated

@pytest.mark.asyncio
async def test_activity_websocket(test_client, mongo_db, headers, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)

    # Edit bio 20 times to fill up the activity queue
    for _ in range(20):
        response = await test_client.post("users/bio", json={"bio": "test"}, headers=headers)
        assert response.status_code == 200

    influence_body = {"beatmaps": [], "influenced_to": 418699,
                      "type": 1, "description": "hi"}
    response = await test_client.post("influence", json=influence_body, headers=headers)
    assert response.status_code == 200

    response = await test_client.post("users/add_beatmap", json={"id": 131891, "is_beatmapset": False}, headers=headers)
    assert response.status_code == 200

    async with aconnect_ws("ws://test/ws", test_client) as ws:
        # Initial connection
        response = await ws.receive_json()
        assert len(response) == 10
        assert_edit_bio(response[0], "test")
        assert_add_influence(response[8], 418699)
        assert_add_beatmap(response[9], {"id": 131891, "is_beatmapset": False})

        # Spontaneous activity
        response = await test_client.post("users/add_beatmap", json={"id": 2117273, "is_beatmapset": False}, headers=headers)
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_add_beatmap(response, {"id": 2117273, "is_beatmapset": False})

        influence_body = {"beatmaps": [], "influenced_to": 8640970,
                          "type": 1, "description": "hi"}
        response = await test_client.post("influence", json=influence_body, headers=headers)
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_add_influence(response, 8640970)

        response = await test_client.post("users/bio", json={"bio": "test2"}, headers=headers)
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_edit_bio(response, "test2")
