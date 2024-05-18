from typing import Annotated, Optional
from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, Beatmap, Influence, get_mongo_db
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/influence", tags=["influence"])


class InfluenceRequest(BaseModel):
    influenced_to: int
    type: int = 1
    description: Optional[str] = None
    beatmaps: Optional[Beatmap] = None


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    return decode_jwt(user_token)


@router.post("", summary="Adds an influence.")
async def add_influence(
        influence_request: InfluenceRequest,
        user: Annotated[dict, Depends(decode_user_token)],
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    influence = Influence(
        influenced_by=user["id"],
        influenced_to=influence_request.influenced_to,
        description=influence_request.description,
        beatmaps=influence_request.beatmaps
    )
    await mongo_db.add_user_influence(influence=influence)


@router.get("/get_influences/{user_id}", response_model=list[Influence], summary="Get all influences of user")
async def get_influences(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_influences(user_id)


@router.delete("/remove_influence/{infuenced_to}", summary="Remove influence")
async def remove_influence(
        user: Annotated[dict, Depends(decode_user_token)],
        influenced_to: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    await mongo_db.remove_user_influence(user["id"], influenced_to)
