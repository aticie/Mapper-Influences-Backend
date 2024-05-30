import asyncio
from datetime import timedelta
import aiohttp
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
import pytest

from app.routers.influence import get_user_osu
from app.utils.jwt import obtain_jwt

from ..main import app
from app.config import settings
from app.db.instance import close_mongo_client, start_mongo_client


async def get_osu_credentials_grant_token():
    token_url = "https://osu.ppy.sh/oauth/token"
    async with aiohttp.ClientSession() as session:
        async with session.post(
                token_url,
                json={
                    "client_id": settings.OSU_CLIENT_ID,
                    "client_secret": settings.OSU_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                    "scope": "identify public",
                },
        ) as response:
            return await response.json()


async def get_authentication_jwt():
    access_token = await get_osu_credentials_grant_token()
    # Can't get /me endpoint to work with client credentials grant type.
    user_details = await get_user_osu(access_token["access_token"], settings.TEST_USER_ID)
    user = {
        "id": user_details["id"],
        "avatar_url": user_details["avatar_url"],
        "username": user_details["username"],
        "country": user_details["country"]["code"],
    }
    user["access_token"] = access_token["access_token"]
    jwt_token = obtain_jwt(
        user, expires_delta=timedelta(seconds=access_token["expires_in"]))
    return jwt_token


# pytest warning says that this is deprecated.
# But I can't find a better way to fix event loop closed error.
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
def setup():
    FastAPICache.init(InMemoryBackend())
    start_mongo_client(settings.MONGODB_URL)
    yield
    close_mongo_client()


@pytest.fixture(scope='session', autouse=True)
def headers():
    jwt = asyncio.run(get_authentication_jwt())
    headers = {"Cookie": f"user_token={jwt}"}
    yield headers


@pytest.fixture(scope='session', autouse=True)
def test_client():
    yield AsyncClient(app=app, base_url="https://test")


@pytest.fixture(scope='session', autouse=True)
def test_user_id():
    yield settings.TEST_USER_ID
