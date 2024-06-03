from typing import Annotated, Optional
import logging
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Cookie, Request, Response
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from app.routers import request_key_builder
from app.utils.jwt import decode_jwt
from app.utils.osu_requester import Requester

OSU_API_BEATMAP_CACHE_EXPIRE = 12*60*60
OSU_API_USER_CACHE_EXPIRE = 3*60*60
OSU_API_SEARCH_CACHE_EXPIRE = 10*60
OSU_API_CACHE_NAMESPACE = "osu_api"


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/osu_api", tags=["osu! API"])


class ConfiguredModel(BaseModel):
    class Config:
        extra = 'ignore'


class BaseUser(ConfiguredModel):
    id: int


class Country (ConfiguredModel):
    code: str
    name: str


class Group(ConfiguredModel):
    colour: Optional[str]
    name: str
    short_name: str


class UserOsu(BaseUser):
    username: str
    avatar_url: str
    country: Country
    groups: list[Group]
    previous_usernames: list[str]
    ranked_and_approved_beatmapset_count: int
    ranked_beatmapset_count: int
    nominated_beatmapset_count: int
    guest_beatmapset_count: int
    loved_beatmapset_count: int
    graveyard_beatmapset_count: int
    pending_beatmapset_count: int


class OsuSearchUserData(ConfiguredModel):
    data: list[BaseUser]


class OsuSearchResponse(ConfiguredModel):
    user: OsuSearchUserData


class BeatmapOsu(ConfiguredModel):
    difficulty_rating: float
    id: int
    mode: str
    beatmapset_id: int
    version: str


class BeatmapsetRelatedUser(ConfiguredModel):
    username: str
    avatar_url: str


class Cover(ConfiguredModel):
    cover: str


class BaseBeatmapset(ConfiguredModel):
    beatmaps: list[BeatmapOsu]
    title: str
    artist: str
    covers: Cover
    creator: str
    id: int
    user_id: int


class BeatmapsetOsu(BaseBeatmapset):
    related_users: list[BeatmapsetRelatedUser]


class OsuSearchMapResponse(ConfiguredModel):
    beatmapsets: list[BaseBeatmapset]


def get_access_token(
        user_token: Annotated[str, Cookie()],
):
    user = decode_jwt(user_token)
    return user["access_token"]


@router.get("/beatmap/{id}", response_model=BeatmapsetOsu, summary="get beatmapset data using osu api. Use type=beatmap to get beatmap data")
@cache(namespace=OSU_API_CACHE_NAMESPACE, expire=OSU_API_BEATMAP_CACHE_EXPIRE, key_builder=request_key_builder)
async def get_beatmapset(
        id: int,
        access_token: Annotated[str, Depends(get_access_token)],
        requester: Requester = Depends(Requester.get_instance),
        type: str | None = None,
):
    if type == "beatmapset" or type is None:
        return await get_beatmapset_osu_parsed(requester, access_token, id)
    elif type == "beatmap":
        beatmap = await get_beatmap_osu_parsed(requester, access_token, id)
        return await get_beatmapset_osu_parsed(requester, access_token, beatmap.beatmapset_id)
    else:
        raise HTTPException(
            status_code=400, detail="Invalid type, type can be 'beatmap' or 'beatmapset'")


@router.get("/user/{user_id}", response_model=UserOsu, summary="get user data using osu api")
@cache(namespace=OSU_API_CACHE_NAMESPACE, expire=OSU_API_USER_CACHE_EXPIRE, key_builder=request_key_builder)
async def get_user(
        user_id: int,
        access_token: Annotated[str, Depends(get_access_token)],
        requester: Requester = Depends(Requester.get_instance),
):
    return await get_user_osu_parsed(requester, access_token, user_id)


@router.get("/search/{query}", response_model=OsuSearchResponse, summary="search users using osu api")
@cache(namespace=OSU_API_CACHE_NAMESPACE, expire=OSU_API_SEARCH_CACHE_EXPIRE, key_builder=request_key_builder)
async def search(
        query: str,
        access_token: Annotated[str, Depends(get_access_token)],
        requester: Requester = Depends(Requester.get_instance),
):
    return await search_user_osu_parsed(requester, access_token, query)


@router.get("/search_map", response_model=OsuSearchMapResponse, summary="search beatmaps using osu api")
@cache(namespace=OSU_API_CACHE_NAMESPACE, expire=OSU_API_SEARCH_CACHE_EXPIRE, key_builder=request_key_builder)
async def search_map(
        access_token: Annotated[str, Depends(get_access_token)],
        request: Request,
        requester: Requester = Depends(Requester.get_instance),
):
    return await search_map_osu_parsed(requester, access_token, str(request.query_params))


async def get_beatmap_osu_parsed(requester: Requester, access_token: str, beatmap_id: int):
    beatmap_url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", BeatmapOsu, beatmap_url, auth_header)


async def get_beatmapset_osu_parsed(requester: Requester, access_token: str, beatmapset_id: int):
    beatmapset_url = f"https://osu.ppy.sh/api/v2/beatmapsets/{beatmapset_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", BeatmapsetOsu, beatmapset_url, auth_header)


async def get_user_osu_parsed(requester: Requester, access_token: str, user_id: int):
    user_url = f"https://osu.ppy.sh/api/v2/users/{user_id}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", UserOsu, user_url, auth_header)


async def search_user_osu_parsed(requester: Requester, access_token: str, query: str):
    search_url = f"https://osu.ppy.sh/api/v2/search/?mode=user&query={query}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", OsuSearchResponse, search_url, auth_header)


async def search_map_osu_parsed(requester: Requester, access_token: str, query: str):
    search_url = f"https://osu.ppy.sh/api/v2/beatmapsets/search?{query}"
    auth_header = {"Authorization": f"Bearer {access_token}"}
    return await requester.request("GET", OsuSearchMapResponse, search_url, auth_header)
