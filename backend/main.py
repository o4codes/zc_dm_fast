from fastapi import FastAPI
from utils.db_handler import *
from core.config import settings
from starlette.middleware.cors import CORSMiddleware
from endpoints import rooms, members, messages, threads
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}



app.include_router(
    messages.router, prefix=settings.API_V1_STR, tags=["messages"]
)  # include urls from message.py
app.include_router(
    rooms.router, prefix=settings.API_V1_STR, tags=["rooms"]
)  # include urls from rooms.py
app.include_router(
    threads.router, prefix=settings.API_V1_STR, tags=["threads"]
)  # include urls from threads.py
app.include_router(
    members.router, prefix=settings.API_V1_STR, tags=["members"]
)  # inlude urls from members.py

app.mount("/", StaticFiles(directory="../frontend", html = True), name="static")