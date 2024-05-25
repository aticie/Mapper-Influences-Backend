import base64
import logging
from typing import Any
from app.db import BaseAsyncMongoClient, Beatmap, Influence

logger = logging.getLogger(__name__)


class InfluenceMongoClient(BaseAsyncMongoClient):
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

    async def get_influences(self, user_id: int):
        logger.debug(f"Getting user influences of {user_id}")
        influences = await self.influences_collection.find({"influenced_by": user_id}, {"_id": False}).to_list(length=None)
        logger.debug(f"User influences of {user_id}: {influences}")
        return influences

    async def get_mentions(self, user_id: int):
        logger.debug(f"Getting user mentions of {user_id}")
        mentions = await self.influences_collection.find({"influenced_to": user_id}, {"_id": False}).to_list(length=None)
        logger.debug(f"User mentions of {user_id}: {mentions}")
        return mentions

    async def get_mention_count(self, user_id: int):
        logger.debug(f"Getting user mention count of {user_id}")
        return await self.influences_collection.count_documents({"influenced_to": user_id})
