from typing import Optional

import aiohttp
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings
from app.db.mongo import AsyncMongoClient
from app.utils.jwt import obtain_jwt

router = APIRouter(prefix="/oauth", tags=["oauth"])
mongo_db = AsyncMongoClient(settings.MONGODB_URL)


@router.get("/osu-redirect", summary="Handles OAuth redirect from osu!.")
async def osu_oauth2_redirect(
        code: str
):
    redirect_response = RedirectResponse("http://localhost:8000/docs")
    access_token = await get_osu_auth_token(code=code)
    user = await get_osu_user(access_token["access_token"])
    db_user = await mongo_db.create_user(user_details=user)
    jwt_token = obtain_jwt(db_user)
    redirect_response.set_cookie(key="user_token", value=jwt_token, httponly=True)

    return redirect_response


async def get_osu_user(access_token: str):
    me_url = "https://osu.ppy.sh/api/v2/me"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(me_url) as response:
            return await response.json()


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
