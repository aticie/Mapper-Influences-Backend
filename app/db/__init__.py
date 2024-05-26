import datetime
import logging
from typing import Optional, Annotated, Any, Callable

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema

logger = logging.getLogger(__name__)


class Beatmap(BaseModel):
    is_beatmapset: bool
    id: int


class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types.

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(
                    validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PydanticObjectId = Annotated[
    ObjectId, _ObjectIdPydanticAnnotation
]


class InfluenceDBModel(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    influenced_by: int
    influenced_to: int
    created_at: datetime.datetime = datetime.datetime.now()
    modified_at: datetime.datetime = datetime.datetime.now()
    type: int = 1
    description: Optional[str] = None
    beatmaps: Optional[list[Beatmap]] = []
    ranked: bool = False


class InfluenceResponse(InfluenceDBModel):
    model_config = ConfigDict(populate_by_name=True)


class User(BaseModel):
    id: int
    username: str
    avatar_url: str
    have_ranked_map: bool
    bio: Optional[str] = None
    beatmaps: Optional[list[Beatmap]] = []
    mention_count: Optional[int] = None
    country: str


class BaseAsyncMongoClient(AsyncIOMotorClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_db = self.get_database("MAPPER_INFLUENCES")
        self.users_collection = self.main_db.get_collection("Users")
        self.influences_collection = self.main_db.get_collection("Influences")
        self.real_users_collection = self.main_db.get_collection("RealUsers")
