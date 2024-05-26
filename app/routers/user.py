from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import Beatmap, User
from app.db.instance import get_mongo_db, AsyncMongoClient
from app.utils.jwt import decode_user_token

router = APIRouter(prefix="/users", tags=["users"])


class BeatmapIdType(Enum):
    diff = "diff"
    set = "set"


class RequestBio(BaseModel):
    bio: str


class InfluenceOrderRequest(BaseModel):
    influence_ids: list[str]


@router.get("/me", response_model=User, summary="Gets registered user details from database")
async def get_user_details(
        user: Annotated[dict, Depends(decode_user_token)],
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await get_user_data(user["id"], mongo_db)


@router.get("/{user_id}", response_model=User, summary="Gets user details from database")
async def get_user_by_id(
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await get_user_data(user_id, mongo_db)


@router.post("/bio", summary="Updates user bio")
async def update_user_bio(
        user: Annotated[dict, Depends(decode_user_token)],
        bio: RequestBio,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.update_user_bio(user["id"], bio.bio)


@router.post("/add_beatmap", summary="Add beatmap to user")
async def add_beatmap_to_user(
        user: Annotated[dict, Depends(decode_user_token)],
        beatmap: Beatmap,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    await mongo_db.add_beatmap_to_user(user["id"], beatmap)
    return


@router.delete("/remove_beatmap/{type}/{id}", summary="Remove beatmap from user, type can be 'set' or 'diff'")
async def remove_beatmap_from_user(
        user: Annotated[dict, Depends(decode_user_token)],
        beatmap_id_type: BeatmapIdType,
        beatmap_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    is_beatmapset = True
    if beatmap_id_type == BeatmapIdType.diff:
        is_beatmapset = False

    await mongo_db.remove_beatmap_from_user(user["id"], beatmap_id, is_beatmapset)
    return


@router.post("/influence-order",
             summary="Set the custom influence order for the current user")
async def save_custom_order(
        user: Annotated[dict, Depends(decode_user_token)],
        influence_order: InfluenceOrderRequest,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    user_id = user["id"]
    return await mongo_db.set_influence_order(user_id, influence_order.influence_ids)


async def get_user_data(user_id: int, mongo_db: AsyncMongoClient):
    result = await mongo_db.get_user_details(user_id)
    count = await mongo_db.get_mention_count(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    result["mention_count"] = count
    return result
