from typing import Optional
from app.db.influence import InfluenceMongoClient
from app.db.leaderboard import LeaderboardMongoClient
from app.db.real_user import RealUserMongoClient
from app.db.user import UserMongoClient


class AsyncMongoClient(
    UserMongoClient, InfluenceMongoClient, LeaderboardMongoClient, RealUserMongoClient
):
    pass


# singleton mongo client
mongo_client: Optional[AsyncMongoClient] = None


def start_mongo_client(mongo_url: str):
    global mongo_client
    mongo_client = AsyncMongoClient(mongo_url)


def close_mongo_client():
    if mongo_client is not None:
        mongo_client.close()


def get_mongo_db() -> AsyncMongoClient:
    return mongo_client
