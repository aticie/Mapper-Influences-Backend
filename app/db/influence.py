import logging

import pymongo

from app.db import BaseAsyncMongoClient, InfluenceDBModel

logger = logging.getLogger(__name__)


class InfluenceMongoClient(BaseAsyncMongoClient):
    async def add_user_influence(self, influence: InfluenceDBModel):
        logger.debug(f"Adding influence: {influence}")
        update_result = await self.influences_collection.update_one(
            {"influenced_by": influence.influenced_by,
             "influenced_to": influence.influenced_to},
            {"$set": influence.model_dump()},
            upsert=True)
        return update_result.upserted_id

    async def remove_user_influence(self, influenced_by: int, influenced_to: int):
        logger.debug(f"Removing influence: {influenced_by} -> {influenced_to}")
        return await self.influences_collection.delete_one(
            {"influenced_by": influenced_by, "influenced_to": influenced_to})

    async def get_influences(self, user_id: int):
        logger.debug(f"Getting user influences of {user_id}")
        influences = await (self.influences_collection.find({"influenced_by": user_id})
                            .sort([("type", pymongo.DESCENDING), ("modified_at", pymongo.DESCENDING)])
                            .to_list(length=None))
        user = await self.users_collection.find_one({"id": user_id})
        sorted_influences = influences.copy()
        if "influence_order" in user:
            influence_order = user["influence_order"]
            # Create a mapping of id to its order position
            order_index = {inf_id: index for index, inf_id in enumerate(influence_order)}

            # Sort the objects based on the order list
            sorted_influences = sorted(influences, key=lambda inf: order_index[inf.id])
        logger.debug(f"User influences of {user_id}: {sorted_influences}")
        return sorted_influences

    async def get_mentions(self, user_id: int):
        logger.debug(f"Getting user mentions of {user_id}")
        mentions = await self.influences_collection.find({"influenced_to": user_id}).to_list(
            length=None)
        logger.debug(f"User mentions of {user_id}: {mentions}")
        return mentions

    async def get_mention_count(self, user_id: int):
        logger.debug(f"Getting user mention count of {user_id}")
        return await self.influences_collection.count_documents({"influenced_to": user_id})
