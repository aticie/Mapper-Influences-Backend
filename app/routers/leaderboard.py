from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_cache.decorator import cache

from app.db.instance import get_mongo_db, AsyncMongoClient

LEADERBOARD_CACHE_EXPIRE = 60
LEADERBOARD_CACHE_NAMESPACE = "leaderboard"

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardResponseUser(BaseModel):
    id: int
    username: str
    avatar_url: str
    country: str
    have_ranked_map: bool
    mention_count: int


class LeaderboardResponse(BaseModel):
    data: list[LeaderboardResponseUser]
    count: int


@router.get(
    "",
    response_model=LeaderboardResponse,
    summary="Get top users which are most mentioned by others",
)
@cache(namespace=LEADERBOARD_CACHE_NAMESPACE, expire=LEADERBOARD_CACHE_EXPIRE)
async def get_leaderboard(
    country: str = None,
    limit: int = None,
    skip: int = None,
    ranked: bool = False,
    type: int = None,
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
) -> LeaderboardResponse:
    return await mongo_db.get_leaderboard(ranked, country, skip, limit, type)
