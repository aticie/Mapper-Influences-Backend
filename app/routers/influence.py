from typing import Annotated, Optional
from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, Beatmap, Influence
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/influence", tags=["influence"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


class InfluenceRequest(BaseModel):
    influenced_to: int
    type: int = 1
    description: Optional[str] = None
    beatmaps: Optional[Beatmap] = None


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    return decode_jwt(user_token)


@router.post("/", summary="Adds an influence.")
async def add_influence(
        influence_request: InfluenceRequest,
        user: Annotated[dict, Depends(decode_user_token)]
):
    influence = Influence(
        influenced_by=user["id"],
        influenced_to=influence_request.influenced_to,
        description=influence_request.description,
        beatmaps=influence_request.beatmaps
    )
    await mongo_db.add_user_influence(
        influence=influence)
    return
