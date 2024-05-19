from typing import Annotated, Dict

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Cookie, Request

from app.utils.jwt import decode_jwt

router = APIRouter(prefix="/osu_api", tags=["osu Api"])


def get_access_token(
        user_token: Annotated[str, Cookie()],
):
    user = decode_jwt(user_token)
    return user["access_token"]


@router.get("/beatmap/{id}", summary="get beatmapset data using osu api. Use type=beatmap to get beatmap data")
async def get_beatmapset(
        id: int,
        access_token: Annotated[str, Depends(get_access_token)],
        type: str | None = None,
):
    if type == "beatmapset" or type is None:
        return await get_beatmapset_osu(access_token, id)
    elif type == "beatmap":
        beatmap = await get_beatmap_osu(access_token, id)
        return await get_beatmapset_osu(access_token, beatmap["beatmapset_id"])
    else:
        raise HTTPException(
            status_code=400, detail="Invalid type, type can be 'beatmap' or 'beatmapset'")


@router.get("/user/{user_id}", summary="get user data using osu api")
async def get_user(
        user_id: int,
        access_token: Annotated[str, Depends(get_access_token)],
):
    return await get_user_osu(access_token, user_id)


@router.get("/user_beatmaps/{beatmap_id}/{type}", summary="get user beatmap data using osu api")
async def get_user_beatmap(
        beatmap_id: int,
        type: str,
        access_token: Annotated[str, Depends(get_access_token)],
):
    return await get_user_beatmaps_osu(access_token, beatmap_id, type)


@router.get("/search/{query}", summary="search users using osu api")
async def search(
        query: str,
        access_token: Annotated[str, Depends(get_access_token)],
):
    response_body = await search_user_osu(access_token, query)
    return response_body["user"]["data"]


@router.get("/search_map", summary="search beatmaps using osu api")
async def search_map(
        access_token: Annotated[str, Depends(get_access_token)],
        request: Request,
):
    response_body = await search_map_osu(access_token, str(request.query_params))
    return response_body["beatmapsets"]


async def get_beatmap_osu(access_token: str, beatmap_id: int):
    beatmap_url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(beatmap_url) as response:
            return await response.json()


async def get_beatmapset_osu(access_token: str, beatmapset_id: int):
    beatmapset_url = f"https://osu.ppy.sh/api/v2/beatmapsets/{beatmapset_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(beatmapset_url) as response:
            return await response.json()


async def get_user_osu(access_token: str, user_id: int):
    user_url = f"https://osu.ppy.sh/api/v2/users/{user_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(user_url) as response:
            return await response.json()


async def get_user_beatmaps_osu(access_token: str, user_id: int, type: str):
    user_maps_url = f"""https://osu.ppy.sh/api/v2/users
                      /{user_id}/beatmapsets/{type}"""
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(user_maps_url) as response:
            return await response.json()


async def search_user_osu(access_token: str, query: str):
    search_url = f"https://osu.ppy.sh/api/v2/search/?mode=user&query={query}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(search_url) as response:
            return await response.json()


async def search_map_osu(access_token: str, query: str):
    search_url = f"https://osu.ppy.sh/api/v2/beatmapsets/search?{query}"
    print(search_url)
    auth_header = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession(headers=auth_header) as session:
        async with session.get(search_url) as response:
            return await response.json()
