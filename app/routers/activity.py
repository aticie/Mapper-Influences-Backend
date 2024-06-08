import asyncio
import datetime
from enum import Enum
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.db import Beatmap, User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    activity_tracker = await ActivityWebsocket.get_instance()
    await activity_tracker.add_connection(websocket)

    try:
        # I guess we need this to track disconnects
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await activity_tracker.remove_connection(websocket)
        return


class ActivityType(Enum):
    EDIT_BIO = "EDIT_BIO"
    ADD_BEATMAP = "ADD_BEATMAP"
    ADD_INFLUENCE = "ADD_INFLUENCE"


class ActivityUser(BaseModel):
    id: int
    username: str
    avatar_url: str
    country: str


class ActivityDetails(BaseModel):
    influenced_to: Optional[ActivityUser] = None
    beatmap: Optional[Beatmap] = None
    description: Optional[str] = None


class Activity(BaseModel):
    type: ActivityType
    user: ActivityUser
    datetime: datetime.datetime
    details: ActivityDetails


class ActivityWebsocket:
    _instance = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        '''To be able to use asyncio lock'''
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = ActivityWebsocket()
                    cls._instance.connections = []
                    cls._instance.activity_queue = []
                    cls._instance.queue_size = 20
        return cls._instance

    def clear_queue(self):
        self.activity_queue = []

    async def add_connection(self, websocket: WebSocket):
        '''Immidiately sends activities to new clients.'''
        self.connections.append(websocket)
        await websocket.send_json(self.activity_queue)

    async def remove_connection(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, activity):
        for connection in self.connections:
            await connection.send_json(activity)

    async def collect_acitivity(self, type: ActivityType, user_data: dict, details: ActivityDetails):
        '''Add latest activity to the queue and broadcast it to all clients.'''

        for activity in self.activity_queue:
            # We only want one update for bio change
            if activity["type"] == type.value and activity["user"]["id"] == user_data["id"]:
                if activity["type"] == "EDIT_BIO":
                    return
                # We only want one update if the user added the same beatmap
                if activity["type"] == "ADD_BEATMAP" and activity["details"]["beatmap"]["id"] == details.beatmap.id:
                    return
                # We only want one update if the user added the same influence
                if activity["type"] == "ADD_INFLUENCE" and activity["details"]["influenced_to"]["id"] == details.influenced_to.id:
                    return

        user = ActivityUser.model_validate(user_data)
        activity = Activity(
            type=type,
            user=user,
            datetime=datetime.datetime.now(),
            details=details
        )
        activity = activity.model_dump(mode="json")
        self.activity_queue.append(activity)
        if len(self.activity_queue) > self.queue_size:
            self.activity_queue.pop(0)
        await self.broadcast(activity)
