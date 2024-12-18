from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import sentry_sdk
import tracemalloc


from app.db.instance import close_mongo_client, start_mongo_client
from app.routers import (
    activity,
    auth,
    influence,
    osu_api_full_response,
    user,
    leaderboard,
    osu_api,
)
from app.config import settings
from app.utils.osu_requester import Requester

logger = logging.getLogger(__name__)

tracemalloc.start()
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring..
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    requester = await Requester.get_instance()
    start_mongo_client(settings.MONGO_URL)
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    close_mongo_client()
    await requester.close()


app = FastAPI(lifespan=lifespan)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(influence.router)
app.include_router(user.router)
app.include_router(leaderboard.router)
app.include_router(osu_api.router)
app.include_router(osu_api_full_response.router)
app.include_router(activity.websocket_router)
app.include_router(activity.http_router)
