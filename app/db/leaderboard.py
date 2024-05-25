import logging
from typing import Union
from app.db import BaseAsyncMongoClient

logger = logging.getLogger(__name__)


class LeaderboardMongoClient(BaseAsyncMongoClient):
    async def get_leaderboard(self, ranked: bool, country_code: str | None, skip: int | None, limit: int | None):
        logger.debug("Getting leaderboard")

        pipeline = [
            {"$lookup": {
                "from": "Users",
                "localField": "influenced_to",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
        ]

        if ranked:
            pipeline.append({"$match": {"user.have_ranked_map": True}})

        pipeline.append({"$group": {
            "_id": "$influenced_to",
            "user_id": {"$first": "$user.id"},
            "username": {"$first": "$user.username"},
            "avatar_url": {"$first": "$user.avatar_url"},
            "country": {"$first": "$user.country"},
            "have_ranked_map": {"$first": "$user.have_ranked_map"},
            "mention_count": {"$sum": 1}
        }})

        pipeline.append({"$sort": {"mention_count": -1}})
        pipeline.append({"$project": {
            "_id": 0,
            "id": "$user_id",
            "username": 1,
            "avatar_url": 1,
            "country": 1,
            "have_ranked_map": 1,
            "mention_count": 1,
        }})

        if country_code is not None:
            pipeline.append({"$match": {"country": country_code}})

        pipeline.append({"$limit": (skip or 0) + (limit or 25)})
        pipeline.append({"$skip": skip or 0})

        return await self.influences_collection.aggregate(pipeline).to_list(length=None)
