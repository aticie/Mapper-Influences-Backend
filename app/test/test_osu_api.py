import pytest


@pytest.mark.asyncio
async def test_osu_api_user(test_client, headers, test_user_id):
    response = await test_client.get(f"osu_api/user/{test_user_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_osu_api_beatmap(test_client, headers):
    response = await test_client.get(f"osu_api/beatmap/131891?type=beatmap", headers=headers)
    assert response.status_code == 200
    response = await test_client.get(f"osu_api/beatmap/41823", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_osu_api_search(test_client, headers):
    response = await test_client.get(f"osu_api/search/heyronii", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_osu_api_search_map(test_client, headers):
    response = await test_client.get(f"osu_api/search_map?q=hi", headers=headers)
    assert response.status_code == 200
