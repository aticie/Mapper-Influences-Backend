import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, influence, user, leaderboard

logger = logging.getLogger(__name__)


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(influence.router)
app.include_router(user.router)
app.include_router(leaderboard.router)
