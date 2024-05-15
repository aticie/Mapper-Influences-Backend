from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import settings
from app.db.mongo import AsyncMongoClient, User
from app.utils.jwt import decode_jwt, decode_user_token

router = APIRouter(prefix="/users", tags=["users"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/me", summary="Gets registered user details from database", response_model=User)
async def get_user_details(
        user: Annotated[dict, Depends(decode_user_token)]
):
    return user
