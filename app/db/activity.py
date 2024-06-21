import logging
from app.db import BaseAsyncMongoClient

logger = logging.getLogger(__name__)


class ActivityMongoClient(BaseAsyncMongoClient):
    async def save_activity(self, activity):
        logger.debug(
            f"Adding activity to database: {activity["user"]["id"]}-{activity["user"]["username"]}-{activity["type"]}"
        )
        await self.activity_collection.insert_one(activity)

    async def get_latest_activities(self, length):
        data = (
            await self.activity_collection.find({}, {"_id": 0})
            .sort("_id", -1)
            .limit(length)
            .to_list(length=length)
        )
        return data
