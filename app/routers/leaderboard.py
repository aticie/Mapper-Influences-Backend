from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_cache.decorator import cache

from app.db.mongo import AsyncMongoClient, get_mongo_db

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardResponseUser(BaseModel):
    id: int
    username: str
    avatar_url: str
    country: str
    have_ranked_map: bool
    mention_count: int


@router.get("", response_model=list[LeaderboardResponseUser], summary="Get top users which are most mentioned by others")
@cache(namespace="leaderboard", expire=60)
async def get_leaderboard(
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
):
    return await mongo_db.get_leaderboard()


@router.get("/ranked", response_model=list[LeaderboardResponseUser], summary="Get top users which are mentioned by ranked mappers")
@cache(namespace="osu_api", expire=60)
async def get_leaderboard(
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
):
    return await mongo_db.get_ranked_leaderboard()
