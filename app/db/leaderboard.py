import logging
from app.db import BaseAsyncMongoClient

logger = logging.getLogger(__name__)


class LeaderboardMongoClient(BaseAsyncMongoClient):
    async def get_leaderboard(self):
        logger.debug("Getting leaderboard")
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
                "have_ranked_map": {"$first": "$user.have_ranked_map"},
                "mention_count": {"$sum": 1}
            }},
            {"$sort": {"mention_count": -1}},
            {"$limit": 25},
            {"$project": {
                "_id": 0,
                "id": "$user_id",
                "username": 1,
                "avatar_url": 1,
                "country": 1,
                "have_ranked_map": 1,
                "mention_count": 1,
            }}
        ]).to_list(length=None)

    async def get_ranked_leaderboard(self):
        logger.debug("Getting ranked leaderboard")
        return await self.influences_collection.aggregate([
            {"$lookup": {
                "from": "Users",
                "localField": "influenced_to",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$match": {"ranked": True}},
            {"$group": {
                "_id": "$influenced_to",
                "user_id": {"$first": "$user.id"},
                "username": {"$first": "$user.username"},
                "avatar_url": {"$first": "$user.avatar_url"},
                "country": {"$first": "$user.country"},
                "have_ranked_map": {"$first": "$user.have_ranked_map"},
                "mention_count": {"$sum": 1}
            }},
            {"$sort": {"mention_count": -1}},
            {"$limit": 25},
            {"$project": {
                "_id": 0,
                "id": "$user_id",
                "username": 1,
                "avatar_url": 1,
                "country": 1,
                "have_ranked_map": 1,
                "mention_count": 1,
            }}
        ]).to_list(length=None)
