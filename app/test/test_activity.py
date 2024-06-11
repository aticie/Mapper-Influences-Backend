import pytest
from httpx_ws import aconnect_ws

from app.routers.activity import ActivityWebsocket
from app.test.helpers import add_fake_user_to_db


def assert_edit_bio(data, description):
    assert data["type"] == "EDIT_BIO"
    assert data["details"]["description"] == description
    assert data["details"]["beatmap"] is None
    assert data["details"]["influenced_to"] is None


def assert_add_beatmap(data, beatmap):
    assert data["type"] == "ADD_BEATMAP"
    assert data["details"]["description"] is None
    assert data["details"]["beatmap"] == beatmap
    assert data["details"]["influenced_to"] is None


def assert_add_influence(data, influenced_to):
    assert data["type"] == "ADD_INFLUENCE"
    assert data["details"]["description"] == "hi"
    assert data["details"]["beatmap"] is None
    assert data["details"]["influenced_to"]["id"] == influenced_to


@pytest.mark.asyncio
async def test_activity_websocket(test_client, mongo_db, headers, test_user_id):
    await add_fake_user_to_db(mongo_db, test_user_id)

    # Edit bio 20 times (should only show the first one)
    for _ in range(20):
        response = await test_client.post(
            "users/bio", json={"bio": "test"}, headers=headers
        )
        assert response.status_code == 200

    influence_body = {
        "beatmaps": [],
        "influenced_to": 418699,
        "type": 1,
        "description": "hi",
    }

    ## Add influence and remove it. Delete should not be shown.
    response = await test_client.post("influence", json=influence_body, headers=headers)
    assert response.status_code == 200
    response = await test_client.delete("influence/418699", headers=headers)
    assert response.status_code == 200

    response = await test_client.post(
        "users/add_beatmap",
        json={"id": 131891, "is_beatmapset": False},
        headers=headers,
    )
    assert response.status_code == 200
    response = await test_client.delete(
        "users/remove_beatmap/diff/131891", headers=headers
    )
    assert response.status_code == 200

    async with aconnect_ws("ws://test/ws", test_client) as ws:
        # Initial connection
        response = await ws.receive_json()
        assert len(response) == 3
        assert_edit_bio(response[0], "test")
        assert_add_influence(response[1], 418699)
        assert_add_beatmap(response[2], {"id": 131891, "is_beatmapset": False})

        # Clear activity to get fresh data. Activity won't be added to queue if the user and activities are the same.
        ws_manager = await ActivityWebsocket.get_instance()
        ws_manager.clear_queue()

        # Spontaneous activity
        response = await test_client.post(
            "users/add_beatmap",
            json={"id": 2117273, "is_beatmapset": False},
            headers=headers,
        )
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_add_beatmap(response, {"id": 2117273, "is_beatmapset": False})

        influence_body = {
            "beatmaps": [],
            "influenced_to": 8640970,
            "type": 1,
            "description": "hi",
        }
        response = await test_client.post(
            "influence", json=influence_body, headers=headers
        )
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_add_influence(response, 8640970)

        response = await test_client.post(
            "users/bio", json={"bio": "test2"}, headers=headers
        )
        assert response.status_code == 200
        response = await ws.receive_json()
        assert_edit_bio(response, "test2")
