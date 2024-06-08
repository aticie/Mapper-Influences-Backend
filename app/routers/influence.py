from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel

from app.db import Beatmap, InfluenceDBModel, User
from app.db.instance import get_mongo_db, AsyncMongoClient
from app.routers.activity import ActivityDetails, ActivityType, ActivityUser, ActivityWebsocket
from app.routers.osu_api import get_user_osu_parsed
from app.utils.jwt import decode_jwt
from app.utils.osu_requester import Requester

router = APIRouter(prefix="/influence", tags=["influence"])


class InfluenceRequest(BaseModel):
    influenced_to: int
    type: int = 1
    description: Optional[str] = None
    beatmaps: list[Beatmap] = []


def decode_user_token(
        user_token: Annotated[str, Cookie()],
):
    try:
        return decode_jwt(user_token)

    except:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("", summary="Adds an influence.", response_model=InfluenceDBModel)
async def add_influence(
        influence_request: InfluenceRequest,
        user: Annotated[dict, Depends(decode_user_token)],
        mongo_db: AsyncMongoClient = Depends(get_mongo_db),
        requester: Requester = Depends(Requester.get_instance),
        activity_ws: ActivityWebsocket = Depends(
            ActivityWebsocket.get_instance)
):
    db_user = await mongo_db.get_user_details(user["id"])
    influence = InfluenceDBModel(
        influenced_by=user["id"],
        influenced_to=influence_request.influenced_to,
        description=influence_request.description,
        beatmaps=influence_request.beatmaps,
        type=influence_request.type,
        ranked=db_user["have_ranked_map"]
    )
    user_osu = await get_user_osu_parsed(requester, user["access_token"], influence.influenced_to)
    # TODO do better error handling here
    if "error" in user_osu:
        raise HTTPException(status_code=404, detail="User not found on osu!")
    created_user_db = await mongo_db.create_user(user_osu)
    await mongo_db.add_user_influence(influence=influence)

    activity_details = ActivityDetails(
        influenced_to=ActivityUser.model_validate(created_user_db),
        description=influence_request.description
    )
    await activity_ws.collect_acitivity(
        ActivityType.ADD_INFLUENCE, user_data=user, details=activity_details)

    return influence


@router.get("/{user_id}", response_model=list[InfluenceDBModel],
            response_model_by_alias=False,
            summary="Get all influences of user")
async def get_influences(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_influences(user_id)


@router.get("/{user_id}/mentions", response_model=list[InfluenceDBModel],
            response_model_by_alias=False,
            summary="Get all mentions of user, basically the opposite of influences")
async def get_influences(
        _: Annotated[dict, Depends(decode_user_token)],
        user_id: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    return await mongo_db.get_mentions(user_id)


@router.delete("/{influenced_to}", summary="Remove influence from the current user")
async def remove_influence(
        user: Annotated[dict, Depends(decode_user_token)],
        influenced_to: int,
        mongo_db: AsyncMongoClient = Depends(get_mongo_db)
):
    await mongo_db.remove_user_influence(user["id"], influenced_to)
    return
