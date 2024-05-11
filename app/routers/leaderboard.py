from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, Beatmap, Influence
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.post("/", summary="get top users which are influenced by others")
async def add_influence():
    await mongo_db.get_leaderboard()
    return
