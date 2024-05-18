import datetime
import logging
from typing import Any, Optional

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
    beatmaps: Optional[list[Beatmap]] = None


class User(BaseModel):
    id: int
    username: str
    avatar_url: str
    have_ranked_map: bool
    bio: Optional[str] = None
    beatmaps: Optional[list[Beatmap]] = None


class LeaderboardUser(User):
    influence_count: int
    country: str


class AsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_db = self.get_database("MAPPER_INFLUENCES")
        self.users_collection = self.main_db.get_collection("Users")
        self.influences_collection = self.main_db.get_collection("Influences")

    async def get_user_details(self, user_id: id):
        logger.debug(f"Getting user influences of {user_id}")
        return await self.users_collection.find_one({"id": user_id}, {"_id": False})

    async def add_user_influence(self, influence: Influence):
        logger.debug(f"Adding influence: {influence}")
        return await self.influences_collection.update_one(
            {"influenced_by": influence.influenced_by,
             "influenced_to": influence.influenced_to},
            {"$set": influence.model_dump()},
            upsert=True)

    async def remove_user_influence(self, influenced_by: int, influenced_to: int):
        logger.debug(f"Removing influence: {influenced_by} -> {influenced_to}")
        return await self.influences_collection.delete_one({"influenced_by": influenced_by, "influenced_to": influenced_to})

    async def create_user(self, user_details: dict[str, Any]):
        assert "avatar_url" in user_details
        assert "id" in user_details
        assert "username" in user_details
        assert "country" in user_details

        db_user = {
            "id": user_details["id"],
            "avatar_url": user_details["avatar_url"],
            "username": user_details["username"],
            "country": user_details["country"]["code"],
        }
        await self.users_collection.update_one({"id": user_details["id"]}, {"$set": db_user}, upsert=True)
        return db_user

    async def get_influences(self, user_id: int):
        logger.debug(f"Getting user influences of {user_id}")
        return await self.influences_collection.find({"influenced_by": user_id}, {"_id": False}).to_list(length=None)

    async def update_user_bio(self, user_id: int, bio: str):
        await self.users_collection.update_one({"id": user_id}, {"$set": {"bio": bio}}, upsert=True)

    async def add_beatmap_to_user(self, user_id: int, beatmap: Beatmap):
        await self.users_collection.update_one({"id": user_id}, {"$push": {"beatmaps": beatmap.model_dump()}}, upsert=True)

    async def remove_beatmap_from_user(self, user_id: int, beatmap: Beatmap):
        await self.users_collection.update_one(
            {"id": user_id},
            {"$pull": {"beatmaps": beatmap.model_dump()}}
        )

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
                "country": {"$first": "$user.country"},
                "influence_count": {"$sum": 1}
            }},
            {"$sort": {"influence_count": -1}},
            {"$limit": 25},
            {"$project": {
                "_id": 0,
                "id": "$user_id",
                "username": 1,
                "avatar_url": 1,
                "influence_count": 1,
                "country": 1
            }}
        ]).to_list(length=None)


# singleton mongo client
mongo_client: AsyncMongoClient = None


def start_mongo_client(mongo_url: str):
    global mongo_client
    mongo_client = AsyncMongoClient(mongo_url)


def close_mongo_client():
    if mongo_client is not None:
        mongo_client.close()


def get_mongo_db() -> AsyncIOMotorClient:
    return mongo_client
