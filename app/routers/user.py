from typing import Annotated

from fastapi import APIRouter, Cookie, Depends

from app.config import settings
from app.db.mongo import AsyncMongoClient, User
from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/users", tags=["users"])


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    return decode_jwt(user_token)


@router.get("/me", summary="Gets registered user details from database", response_model=User)
async def get_user_details(
        user: Annotated[dict, Depends(decode_user_token)]
):
    return user
