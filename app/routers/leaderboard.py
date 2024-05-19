from fastapi import APIRouter, Depends

from app.db.mongo import AsyncMongoClient, User, get_mongo_db

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("",  summary="Get top users which are most mentioned by others")
async def get_leaderboard(
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
):
    return await mongo_db.get_leaderboard()


@router.get("/ranked", summary="Get top users which are mentioned by ranked mappers")
async def get_leaderboard(
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
):
    return await mongo_db.get_ranked_leaderboard()
