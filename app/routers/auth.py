from datetime import timedelta
import logging
import aiohttp
from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db import User
from app.db.instance import get_mongo_db, AsyncMongoClient
from app.routers.activity import ActivityDetails, ActivityType, ActivityWebsocket
from app.routers.osu_api import UserOsu
from app.utils.jwt import obtain_jwt
from app.utils.osu_requester import Requester

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/osu-redirect", summary="Handles OAuth redirect from osu!.")
async def osu_oauth2_redirect(
        code: str,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db),
        requester: Requester = Depends(Requester.get_instance),
        activity_ws: ActivityWebsocket = Depends(
            ActivityWebsocket.get_instance)
):

    redirect_response = RedirectResponse(settings.POST_LOGIN_REDIRECT_URI)
    access_token = await get_osu_auth_token(code=code)
    user = await get_osu_user(requester, access_token["access_token"])
    await mongo_db.add_real_user(user)
    db_user = await mongo_db.create_user(user_details=user)
    db_user["access_token"] = access_token["access_token"]
    jwt_token = obtain_jwt(
        db_user, expires_delta=timedelta(seconds=access_token["expires_in"]))
    redirect_response.set_cookie(
        key="user_token", value=jwt_token, httponly=True, max_age=access_token["expires_in"])

    await activity_ws.collect_acitivity(
        ActivityType.LOGIN, user_data=db_user, details=ActivityDetails())

    return redirect_response


@router.get("/logout", summary="Logs out the user. (basically removes the cookie)")
async def logout(response: Response):
    response.delete_cookie("user_token")
    return


async def get_osu_user(requester, access_token: str):
    me_url = "https://osu.ppy.sh/api/v2/me"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", UserOsu, me_url, auth_header)


async def get_osu_auth_token(code: str):
    token_url = "https://osu.ppy.sh/oauth/token"
    async with aiohttp.ClientSession() as session:
        async with session.post(
                token_url,
                json={
                    "client_id": settings.OSU_CLIENT_ID,
                    "client_secret": settings.OSU_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.OSU_REDIRECT_URI,
                },
        ) as response:
            return await response.json()
