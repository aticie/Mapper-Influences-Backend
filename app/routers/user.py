from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient, User, get_mongo_db
from app.utils.jwt import decode_user_token

router = APIRouter(prefix="/users", tags=["users"])


class Bio(BaseModel):
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
        bio: Bio,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.update_user_bio(user["id"], bio.bio)
