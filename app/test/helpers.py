
from datetime import timedelta
import aiohttp


from app.routers.influence import get_user_osu
from app.utils.jwt import decode_jwt, obtain_jwt
from app.config import settings


async def get_osu_credentials_grant_token():
    token_url = "https://osu.ppy.sh/oauth/token"
    async with aiohttp.ClientSession() as session:
        async with session.post(
                token_url,
                json={
                    "client_id": settings.OSU_CLIENT_ID,
                    "client_secret": settings.OSU_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                    "scope": "identify public",
                },
        ) as response:
            return await response.json()


async def get_authentication_jwt():
    access_token = await get_osu_credentials_grant_token()
    # Can't get /me endpoint to work with client credentials grant type.
    user_details = await get_user_osu(access_token["access_token"], settings.TEST_USER_ID)
    user = {
        "id": user_details["id"],
        "avatar_url": user_details["avatar_url"],
        "username": user_details["username"],
        "country": user_details["country"]["code"],
    }
    user["access_token"] = access_token["access_token"]
    jwt_token = obtain_jwt(
        user, expires_delta=timedelta(seconds=access_token["expires_in"]))
    return jwt_token


async def add_fake_user_to_db(mongo_db, user_id, test_name: str = "test"):
    '''
    Add a fake user to the database for testing purposes.
    It has to have the same user_id as the one in the headers.
    Other users will be added by the influence endpoint.
    '''
    user_details = {
        "id": user_id,
        "avatar_url": test_name,
        "username": test_name,
        "country": "TR",
        "have_ranked_map": True,
    }
    await mongo_db.users_collection.update_one({"id": user_details["id"]}, {"$set": user_details}, upsert=True)
