from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.instance import AsyncMongoClient, get_mongo_db
from app.routers.osu_api import (
    BeatmapOsuMultiple,
    BeatmapsetOsuMultiple,
    UserOsuMultiple,
)
from app.utils.osu_requester import ApiMultiRequester
from app.utils.jwt import decode_user_token


router = APIRouter(prefix="/v2/osu_api", tags=["V2 endpoints"])


async def user_multi_requester():
    return await ApiMultiRequester.get_instance(UserOsuMultiple)


async def beatmap_multi_requester():
    return await ApiMultiRequester.get_instance(BeatmapOsuMultiple)


async def beatmapset_multi_requester():
    return await ApiMultiRequester.get_instance(BeatmapsetOsuMultiple)


@router.get("/user/{user_id}", summary="get user data using osu api")
async def get_multiple_users(
    user_id: int,
    user: Annotated[str, Depends(decode_user_token)],
    mongo_db: AsyncMongoClient = Depends(get_mongo_db),
    multi_requester: ApiMultiRequester = Depends(beatmapset_multi_requester),
):
    test_data = [user_id]
    # test_data = [873961, 4865030] + [user_id]
    auth_header = {"Authorization": f"Bearer {user["access_token"]}"}
    api_data = await multi_requester.get_data(test_data, auth_header)
    return api_data
