from fastapi import APIRouter

from app.config import settings
from app.db.mongo import AsyncMongoClient, LeaderboardUser

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/", summary="get top users which are influenced by others", response_model=list[LeaderboardUser])
async def get_leaderboard():
    return await mongo_db.get_leaderboard()
