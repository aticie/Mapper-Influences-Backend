from fastapi import APIRouter, Depends

from app.db.mongo import AsyncMongoClient, LeaderboardUser, get_mongo_db

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", summary="get top users which are influenced by others", response_model=list[LeaderboardUser])
async def get_leaderboard(
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_leaderboard()
