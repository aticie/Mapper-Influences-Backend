from fastapi import APIRouter, Cookie, Depends

from app.config import settings
from app.db.mongo import AsyncMongoClient, LeaderboardUser, get_mongo_db
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/", summary="get top users which are influenced by others", response_model=list[LeaderboardUser])
async def get_leaderboard(mongo_db: AsyncMongoClient = Depends(get_mongo_db)):
    return await mongo_db.get_leaderboard()
