import asyncio
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
import pytest

from ..main import app
from app.test.helpers import add_fake_user_to_db, get_authentication_jwt
from app.config import settings
from app.db.instance import close_mongo_client, get_mongo_db, start_mongo_client


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
    yield


@pytest.fixture(scope='session', autouse=True)
def mongo_db():
    start_mongo_client(settings.MONGODB_URL)
    yield get_mongo_db()
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
