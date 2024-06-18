from typing import Annotated
from fastapi import APIRouter, Depends

from app.routers.osu_api import OsuUserMultiple, get_access_token
from app.utils.osu_requester import ApiMultiRequester


router = APIRouter(prefix="/osu_api/test", tags=["osu! API"])


async def user_multi_requester():
    return await ApiMultiRequester.get_instance(OsuUserMultiple)


@router.get("/user/{user_id}", summary="get user data using osu api")
async def get_multiple_users(
    user_id: int,
    access_token: Annotated[str, Depends(get_access_token)],
    multi_requester: ApiMultiRequester = Depends(user_multi_requester),
):
    test_data = [873961, 4865030] + [user_id]
    auth_header = {"Authorization": f"Bearer {access_token}"}
    api_data = await multi_requester.get_data(test_data, auth_header)
    return list(api_data.values())
