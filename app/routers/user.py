from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, Beatmap, User, get_mongo_db
from app.utils.jwt import decode_user_token

router = APIRouter(prefix="/users", tags=["users"])


class BeatmapIdType(Enum):
    diff = "diff"
    set = "set"


class RequestBio(BaseModel):
    bio: str


@router.get("/me", response_model=User, summary="Gets registered user details from database")
async def get_user_details(
        user: Annotated[dict, Depends(decode_user_token)],
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    result = await mongo_db.get_user_details(user["id"])
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/{user_id}", response_model=User, summary="Gets user details from database")
async def get_user_by_id(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    result = await mongo_db.get_user_details(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


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
        type: BeatmapIdType,
        id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    if type == BeatmapIdType.set:
        is_beatmapset = True
    elif type == BeatmapIdType.diff:
        is_beatmapset = False

    await mongo_db.remove_beatmap_from_user(user["id"], id, is_beatmapset)
    return
