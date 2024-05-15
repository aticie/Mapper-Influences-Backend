from typing import Annotated
import aiohttp
from fastapi import APIRouter, Depends

from app.utils.jwt import decode_user_token
from app.utils.encryption import decrypt_string

router = APIRouter(prefix="/osu_api", tags=["osu Api"])


@router.get("/beatmap/{beatmap_id}", summary="get beatmap data using osu api")
async def get_beatmap(
    beatmap_id: int,
    user: Annotated[dict, Depends(decode_user_token)],
):
    access_token = decrypt_string(user["access_token"])
    return await get_beatmap(access_token, beatmap_id)


@router.get("/user/{user_id}", summary="get user data using osu api")
async def get_user(
    user_id: int,
    user: Annotated[dict, Depends(decode_user_token)],
):
    access_token = decrypt_string(user["access_token"])
    return await get_user(access_token, user_id)


@router.get("/user_beatmaps/{beatmap_id}/{type}", summary="get user beatmap data using osu api")
async def get_user_beatmap(
    beatmap_id: int,
    type: str,
    user: Annotated[dict, Depends(decode_user_token)],
):
    access_token = decrypt_string(user["access_token"])
    return await get_user_beatmap(access_token, beatmap_id, type)


async def get_beatmap(access_token: str, beatmap_id: int):
    beatmap_url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(beatmap_url) as response:
            return await response.json()


async def get_user(access_token: str, user_id: int):
    user_url = f"https://osu.ppy.sh/api/v2/users/{user_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(user_url) as response:
            return await response.json()


async def get_user_beatmaps(access_token: str, user_id: int, type: str):
    user_maps_url = f"""https://osu.ppy.sh/api/v2/users
                      /{user_id}/beatmapsets/{type}"""
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(user_maps_url) as response:
            return await response.json()
