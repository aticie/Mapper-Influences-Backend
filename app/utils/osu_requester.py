import asyncio
import logging
import os
from typing import Optional
from dataclasses import dataclass
import aiohttp
from fastapi import HTTPException
from Crypto.Hash import SHA256
from datetime import datetime, timedelta

from app.config import settings


logger = logging.getLogger(__name__)


async def check_response(response: aiohttp.ClientResponse):
    if response.status == 404:
        raise HTTPException(
            status_code=404, detail="Searched item could not be found on osu! API"
        )
    elif response.status != 200:
        logger.error(
            f"Error while fetching data from osu! API: {response.status}: {await response.text()}"
        )
        raise HTTPException(status_code=500)


class Requester:
    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        """To be able to use asyncio lock"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = Requester()
                    cls._instance.test_path = None
                    # Limiting the amount of connections to 10.
                    # This is to prevent osu! API from blocking us for too many concurent requests.
                    # This might fix the random api errors we get.
                    # If doesn't work, just revert it to default by removing the connector.
                    conn = aiohttp.TCPConnector(limit=10)
                    cls._instance.session = aiohttp.ClientSession(connector=conn)
        return cls._instance

    def set_test_path(self, test_path: str):
        self.test_path = test_path

    async def close(self):
        await self.session.close()
        Requester._instance = None

    async def inner_request(
        self, method: str, url: str, headers: dict[str, str] = None, json: dict = None
    ):
        async with self.session.request(
            method, url, headers=headers, json=json
        ) as response:
            await check_response(response)
            return await response.text()

    async def request(
        self,
        method: str,
        type,
        url: str,
        headers: dict[str, str] = None,
        json: dict = None,
    ):
        """
        Basically does a normal request in the production environment, but if the test_path is set,
        it will save the response to a file and return the data from the file.
        Basically mocking the responses for tests. Push the data to github and use it in the tests.
        """

        if self.test_path is None:
            text = await self.inner_request(method, url, headers, json)
            print(text)
            return type.model_validate_json(text)

        os.makedirs(self.test_path, exist_ok=True)
        file_path = os.path.join(self.test_path, f"{method}-{hash_url(url)}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as json_file:
                existing_data = type.model_validate_json(json_file.read())
            return existing_data
        else:
            authenticator = await LazyTestAuthenticator.get_instance()
            text = await self.inner_request(
                method, url, authenticator.as_header(), json
            )
            with open(file_path, "w", encoding="utf-8") as json_file:
                json_file.write(text)
                return type.model_validate_json(text)


class LazyTestAuthenticator:
    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = LazyTestAuthenticator()
                    token_json = await get_osu_credentials_grant_token()
                    cls._instance.access_token = token_json["access_token"]
        return cls._instance

    def as_header(self):
        return {"Authorization": f"Bearer {self.access_token}"}


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


def hash_url(url: str):
    return SHA256.new(data=str.encode(url)).hexdigest()


@dataclass
class CacheItem:
    datetime_added: datetime
    data: any


class Cache:
    def __init__(self, expiration_timedelta: timedelta = timedelta(hours=6)):
        self.cache: dict[int, CacheItem] = {}
        self.expiration_timedelta = expiration_timedelta

    def add_data(self, data_list: any):
        expiration_datetime = datetime.now() + self.expiration_timedelta
        for data in data_list.get_items():
            self.cache[data.id] = CacheItem(expiration_datetime, data)

    def discard_expired_data(self):
        """
        Discard old cache items. Since the dictionaries guaranties insertion order
        We can loop from the start and discard old items like a queue
        We need to have two loops because we can't delete the dict items in one loop
        """
        date_now = datetime.now()
        keys_to_delete = []
        for key, data in self.cache.items():
            if data.datetime_added < date_now:
                keys_to_delete.append(key)
            else:
                break
        for key in keys_to_delete:
            del self.cache[key]

    def get_cache_data(self, key_list: list[int]):
        self.discard_expired_data()
        cache_hit_data: list[any] = []
        cache_miss_keys: list[int] = []
        for key in key_list:
            item = self.cache.get(key)
            if item is None:
                cache_miss_keys.append(key)
            else:
                cache_hit_data.append(item.data)
        return cache_hit_data, cache_miss_keys


class ApiMultiRequester:
    _instances = {}
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls, type, base_url: Optional[str] = None):
        """Be sure to call this first time with base_url"""
        if type not in cls._instances:
            async with cls._lock:
                if type is not cls._instances:
                    instance = ApiMultiRequester()
                    instance.cache: Cache = Cache()
                    instance.requester: Requester = await Requester.get_instance()
                    instance.type = type
                    instance.base_url: Optional[str] = base_url
                    cls._instances[type] = instance
                    return instance
        else:
            return cls._instances.get(type)

    @classmethod
    def print_instances(cls):
        print(len(cls._instances))

    @classmethod
    async def close_all(cls):
        for instance in cls._instances.values():
            await instance.requester.close()
        cls._instances = {}

    async def get_data(self, id_list: list[int], headers: dict[str, str]):
        cache_hit_data, cache_miss_keys = self.cache.get_cache_data(id_list)

        data = {}
        for chunk_start in range(0, len(cache_miss_keys), 50):
            request_chunk_ids = cache_miss_keys[chunk_start : chunk_start + 50]
            url = (
                self.base_url
                + "?"
                + "&".join(["ids[]=" + str(id) for id in request_chunk_ids])
            )
            response = await self.requester.request(
                "GET", self.type, url, headers=headers
            )

            self.cache.add_data(response)

            for item in response.get_items():
                data[item.id] = item

        for item in cache_hit_data:
            data[item.id] = item

        return data
