import base64
import logging
from typing import Any
from app.db import BaseAsyncMongoClient, Beatmap
from app.routers.osu_api import UserOsu

logger = logging.getLogger(__name__)


def has_ranked_beatmapsets(user_data: UserOsu) -> bool:
    final_count = user_data.ranked_beatmapset_count
    final_count += user_data.loved_beatmapset_count
    final_count += user_data.guest_beatmapset_count
    return final_count > 0


class UserMongoClient(BaseAsyncMongoClient):
    async def get_user_details(self, user_id: id):
        logger.debug(f"Getting user influences of {user_id}")
        return await self.users_collection.find_one({"id": user_id}, {"_id": False})

    async def create_user(self, user_details: UserOsu):

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

    async def update_user_bio(self, user_id: int, bio: str):
        logger.debug(f"Updating user bio of {user_id}: {
                     base64.b64encode(bio.encode('UTF-8'))}")
        await self.users_collection.update_one({"id": user_id}, {"$set": {"bio": bio}}, upsert=True)

    async def add_beatmap_to_user(self, user_id: int, beatmap: Beatmap):
        logger.debug(f"Adding beatmap to user {user_id}: {beatmap}")
        await self.users_collection.update_one({"id": user_id}, {"$push": {"beatmaps": beatmap.model_dump()}},
                                               upsert=True)

    async def remove_beatmap_from_user(self, user_id: int, beatmap_id: int, is_beatmapset: bool):
        beatmap = Beatmap(is_beatmapset=is_beatmapset, id=beatmap_id)
        logger.debug(f"Removing beatmap from user {user_id}: {beatmap}")
        await self.users_collection.update_one(
            {"id": user_id},
            {"$pull": {"beatmaps": beatmap.model_dump()}}
        )

    async def set_influence_order(self, user_id: int, influence_ids: list[int]):
        user_id_b64 = base64.b64encode(str(user_id).encode())
        influence_ids_b64 = [base64.b64encode(
            str(inf_id).encode()) for inf_id in influence_ids]
        logger.debug(f"Setting influence order for {
                     user_id_b64=} to {influence_ids_b64=}.")
        await self.users_collection.update_one(
            {"id": user_id},
            {"$set": {"influence_order": influence_ids}}
        )
