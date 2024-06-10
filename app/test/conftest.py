import asyncio
from contextlib import asynccontextmanager
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
import pytest
import pytest_asyncio
from httpx_ws.transport import ASGIWebSocketTransport

from app.utils.osu_requester import Requester

from ..main import app
from app.test.helpers import add_fake_user_to_db, get_authentication_jwt
from app.config import settings
from app.db.instance import close_mongo_client, get_mongo_db, start_mongo_client


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def headers():
    jwt = await get_authentication_jwt()
    headers = {"Cookie": f"user_token={jwt}"}
    yield headers


@pytest_asyncio.fixture(scope="session")
async def test_user_id():
    yield int(settings.TEST_USER_ID)


@pytest_asyncio.fixture(scope="session")
async def mongo_db():
    start_mongo_client(settings.MONGO_URL)
    yield get_mongo_db()
    close_mongo_client()


@pytest_asyncio.fixture
async def lifespan_manager():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        requester = await Requester.get_instance()
        requester.set_test_path("app/test/data")
        start_mongo_client(settings.MONGO_URL)
        FastAPICache.init(InMemoryBackend())
        yield
        close_mongo_client()
        await requester.close()

    app.router.lifespan_context = lifespan

    async with LifespanManager(app) as manager:
        yield manager.app


@pytest_asyncio.fixture
async def test_client(lifespan_manager):
    async with AsyncClient(transport=ASGIWebSocketTransport(lifespan_manager), base_url="https://test") as client:
        yield client

