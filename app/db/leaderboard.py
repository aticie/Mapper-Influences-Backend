import logging
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
            pipeline.append({"$match": {"ranked": True}})

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

        pipeline.append({"$facet": {
            "count": [{"$count": "total"}],
            "data": [{"$limit": (skip or 0) + (limit or 25)}, {"$skip": skip or 0}]

        }})

        result = self.influences_collection.aggregate(pipeline)
        async for doc in result:
            doc["count"] = doc["count"][0]["total"]
            return doc
