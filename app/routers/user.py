from typing import Annotated

from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel

from app.config import settings
from app.db.mongo import AsyncMongoClient
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/users", tags=["users"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


class UserResponse(BaseModel):
    id: int
    username: str
    avatar_url: str


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    return decode_jwt(user_token)


@router.get("/me", response_model=UserResponse, summary="Gets registered user details from database")
async def get_user_details(
        user: Annotated[dict, Depends(decode_user_token)]
):
    return user
