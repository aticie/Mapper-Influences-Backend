import logging
from typing import Any
from app.db import BaseAsyncMongoClient
from app.db.user import has_ranked_beatmapsets
from app.routers.osu_api import UserOsu

logger = logging.getLogger(__name__)


class RealUserMongoClient(BaseAsyncMongoClient):

    # TODO: instead of this, add this to `User` as boolean
    async def add_real_user(self, user_details: UserOsu):

        db_user = {
            "id": user_details.id,
            "avatar_url": user_details.avatar_url,
            "username": user_details.username,
            "country": user_details.country.code,
            "have_ranked_map": has_ranked_beatmapsets(user_details),
        }
        logger.debug(f"Upserting user: {db_user}")
        await self.users_collection.update_one({"id": user_details.id}, {"$set": db_user}, upsert=True)
        return db_user
