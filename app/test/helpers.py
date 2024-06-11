from datetime import timedelta

from app.utils.jwt import obtain_jwt
from app.config import settings


async def get_authentication_jwt():
    user = {
        "id": int(settings.TEST_USER_ID),
        "avatar_url": "https://osu.ppy.sh/images/layout/avatar-guest@2x.png",
        "username": "112servis",
        "country": "TR",
    }
    user["access_token"] = "RandomTestValue"
    jwt_token = obtain_jwt(user, expires_delta=timedelta(seconds=60 * 60))
    return jwt_token


async def add_fake_user_to_db(mongo_db, user_id, test_name: str = "test"):
    """
    Add a fake user to the database for testing purposes.
    It has to have the same user_id as the one in the headers.
    Other users will be added by the influence endpoint.
    """
    user_details = {
        "id": user_id,
        "avatar_url": test_name,
        "username": test_name,
        "country": "TR",
        "have_ranked_map": True,
    }
    await mongo_db.users_collection.update_one(
        {"id": user_details["id"]}, {"$set": user_details}, upsert=True
    )


async def add_fake_influence_to_db(mongo_db, influenced_by, influenced_to):
    """To be able to test mentions endpoint"""
    influence = {
        "influenced_by": influenced_by,
        "influenced_to": influenced_to,
        "description": "test",
        "beatmaps": None,
        "type": 1,
        "ranked": True,
    }
    await mongo_db.influences_collection.insert_one(influence)
