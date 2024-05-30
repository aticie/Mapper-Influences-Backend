import pytest


@pytest.mark.asyncio
async def test_set_user_bio(test_client, headers):
    response = await test_client.post("users/bio", json={"bio": "test"}, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user(test_client, headers, test_user_id):
    response = await test_client.get(f"users/{test_user_id}", headers=headers)
    assert response.status_code == 200
