from typing import Annotated, Optional

import aiohttp
from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel

from app.db import Beatmap, InfluenceDBModel, InfluenceResponse
from app.db.instance import get_mongo_db, AsyncMongoClient
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/influence", tags=["influence"])


class InfluenceRequest(BaseModel):
    influenced_to: int
    type: int = 1
    description: Optional[str] = None
    beatmaps: list[Beatmap] = []


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    return decode_jwt(user_token)


@router.post("", summary="Adds an influence.", response_model=InfluenceResponse)
async def add_influence(
        influence_request: InfluenceRequest,
        user: Annotated[dict, Depends(decode_user_token)],
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    db_user = await mongo_db.get_user_details(user["id"])
    influence = InfluenceDBModel(
        influenced_by=user["id"],
        influenced_to=influence_request.influenced_to,
        description=influence_request.description,
        beatmaps=influence_request.beatmaps,
        type=influence_request.type,
        ranked=db_user["have_ranked_map"]
    )
    user_osu = await get_user_osu(user["access_token"], influence.influenced_to)
    # TODO do better error handling here
    if "error" in user_osu:
        raise HTTPException(status_code=404, detail="User not found on osu!")
    await mongo_db.create_user(user_osu)
    influence_id = await mongo_db.add_user_influence(influence=influence)
    response = InfluenceResponse(**influence.model_dump(), id=influence_id)
    return response


@router.get("/{user_id}", response_model=list[InfluenceResponse],
            response_model_by_alias=False,
            summary="Get all influences of user")
async def get_influences(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_influences(user_id)


@router.get("/{user_id}/mentions", response_model=list[InfluenceResponse],
            response_model_by_alias=False,
            summary="Get all mentions of user, basically the opposite of influences")
async def get_influences(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_mentions(user_id)


@router.delete("/{influenced_to}", summary="Remove influence from the current user")
async def remove_influence(
        user: Annotated[dict, Depends(decode_user_token)],
        influenced_to: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    await mongo_db.remove_user_influence(user["id"], influenced_to)
    return


async def get_user_osu(access_token: str, user_id: int):
    user_url = f"https://osu.ppy.sh/api/v2/users/{user_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(user_url) as response:
            return await response.json()
