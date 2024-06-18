from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import sentry_sdk


from app.db.instance import close_mongo_client, start_mongo_client
from app.routers import (
    activity,
    apiv2test,
    auth,
    influence,
    osu_api_full_response,
    user,
    leaderboard,
    osu_api,
)
from app.config import settings
from app.utils.osu_requester import ApiMultiRequester, Requester

logger = logging.getLogger(__name__)


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
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
    FastAPICache.init(InMemoryBackend())
    # initialize instances with paths here. You can gp
    await ApiMultiRequester.get_instance(
        osu_api.OsuUserMultiple, "https://osu.ppy.sh/api/v2/users"
    )
    await ApiMultiRequester.get_instance(
        osu_api.BeatmapsetOsu, "https://osu.ppy.sh/api/v2/beatmapsets"
    )
    multi_requester = await ApiMultiRequester.get_instance(
        osu_api.BeatmapOsu, "https://osu.ppy.sh/api/v2/beatmaps"
    )
    yield
    close_mongo_client()
    await requester.close()
    await multi_requester.close_all()


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
app.include_router(activity.router)
app.include_router(apiv2test.router)
