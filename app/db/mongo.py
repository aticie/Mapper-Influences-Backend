import datetime
import logging
from typing import Union, Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Beatmap(BaseModel):
    is_beatmapset: bool
    id: int


class Influence(BaseModel):
    influenced_by: int
    influenced_to: int
    created_at: datetime.datetime = datetime.datetime.now()
    modified_at: datetime.datetime = datetime.datetime.now()
    type: int = 1
    description: Optional[str] = None
    beatmaps: Optional[Beatmap] = None


class AsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_db = self.get_database("MAPPER_INFLUENCES")
        self.users_collection = self.main_db.get_collection("Users")
        self.influences_collection = self.main_db.get_collection("Influences")

    async def get_user_details(self, user_id: Union[str, int]):
        logger.debug(f"Getting user influences of {user_id}")
        return await self.main_db.find({"userId": user_id}).to_list(length=None)

    async def add_user_influence(self, influence: Influence):
        logger.debug(f"Adding influence: {influence}")
        return await self.influences_collection.update_one(
            {"influenced_by": influence.influenced_by,
             "influenced_to": influence.influenced_to},
            {"$set": influence.model_dump()},
            upsert=True)

    async def create_user(self, user_details: dict[str, Any]):
        assert "avatar_url" in user_details
        assert "id" in user_details
        assert "username" in user_details

        db_user = {
            "id": user_details["id"],
            "avatar_url": user_details["avatar_url"],
            "username": user_details["username"]
        }
        await self.users_collection.update_one({"id": user_details["id"]}, {"$set": db_user}, upsert=True)
        return db_user

    async def get_leaderboard(self):
        return await self.influences_collection.aggregate([
            {"$lookup": {
                "from": "Users",
                "localField": "influenced_to",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$group": {
                "_id": "$influenced_to",
                "user_id": {"$first": "$user.id"},
                "username": {"$first": "$user.username"},
                "avatar_url": {"$first": "$user.avatar_url"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$project": {
                "_id": 0,
                "id": "$user_id",
                "username": 1,
                "avatar_url": 1,
                "count": 1
            }}
        ]).to_list(length=None)
