import logging
from typing import Any
from app.db import BaseAsyncMongoClient
from app.db.user import has_ranked_beatmapsets

logger = logging.getLogger(__name__)


class RealUserMongoClient(BaseAsyncMongoClient):

    # TODO: instead of this, add this to `User` as boolean
    async def add_real_user(self, user_details: dict[str, Any]):
        logger.debug(f"Adding real user: {user_details}")
        assert "avatar_url" in user_details
        assert "id" in user_details
        assert "username" in user_details
        assert "country" in user_details
        db_user = {
            "id": user_details["id"],
            "avatar_url": user_details["avatar_url"],
            "username": user_details["username"],
            "country": user_details["country"]["code"],
            "have_ranked_map": has_ranked_beatmapsets(user_details),
        }
        await self.real_users_collection.update_one({"id": user_details["id"]}, {"$set": db_user}, upsert=True)
