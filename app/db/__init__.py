

import datetime
import logging
from typing import Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

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
    beatmaps: Optional[list[Beatmap]] = []
    ranked: bool = False


class User(BaseModel):
    id: int
    username: str
    avatar_url: str
    have_ranked_map: bool
    bio: Optional[str] = None
    beatmaps: Optional[list[Beatmap]] = []
    mention_count: Optional[int] = None
    country: str


class BaseAsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_db = self.get_database("MAPPER_INFLUENCES")
        self.users_collection = self.main_db.get_collection("Users")
        self.influences_collection = self.main_db.get_collection("Influences")
        self.real_users_collection = self.main_db.get_collection("RealUsers")
