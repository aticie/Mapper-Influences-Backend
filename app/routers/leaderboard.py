from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, LeaderboardUser
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


class LeaderboardUserResponse(BaseModel):
    id: int
    username: str
    avatar_url: str
    influence_count: int
    country: str


@router.get("/", response_model=list[LeaderboardUserResponse], summary="get top users which are influenced by others")
async def get_leaderboard():
    return await mongo_db.get_leaderboard()
