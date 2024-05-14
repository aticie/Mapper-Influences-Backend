from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongo import close_mongo_client, start_mongo_client
from app.routers import auth, influence, user, leaderboard
from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mongo_client(settings.MONGODB_URL)
    yield
    close_mongo_client()


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
