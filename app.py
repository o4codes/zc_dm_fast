<<<<<<< HEAD
from typing import Optional
from fastapi import FastAPI, status, Response
from utils.db_handler import *
=======
from fastapi import FastAPI, status, HTTPException
from core.config import settings
from starlette.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from endpoints import rooms, members, messages, threads
>>>>>>> 7a4beac228ac328c4f2c6477b24a9e28dde5c250

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


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/api/v1/org/{org_id}/users/{user_id}/rooms", status_code = 200)
async def user_ooms(user_id: str, org_id: str, response: Response):
    """Get the rooms a user is in

    Args:
        user_id (str): The user id

    Returns:
        [List]: [description]
    """
    result = get_rooms(user_id, org_id)

    if result:
        return result
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return result


@app.get("/api/v1/org/{org_id}/rooms/{room_id}/messages", status_code = 200)
async def room_messages(*, org_id: str, room_id: str, date: Optional[str] = None, response: Response):
    if date == None:
        room_messages = get_room_messages(room_id=room_id, org_id=org_id)
        if room_messages:
            return room_messages
        response.status_code = status.HTTP_204_NO_CONTENT
        return room_messages
    messages_by_date = get_messages(room_id, org_id, date)
    if messages_by_date:
        return messages_by_date
    response.status_code = status.HTTP_204_NO_CONTENT
    return messages_by_date
app.include_router(messages.router, prefix=settings.API_V1_STR, tags=["messages"]) # include urls from message.py
app.include_router(rooms.router, prefix=settings.API_V1_STR, tags=["rooms"]) # include urls from rooms.py
app.include_router(threads.router, prefix=settings.API_V1_STR, tags=["threads"]) # include urls from threads.py
app.include_router(members.router, prefix=settings.API_V1_STR, tags=["members"]) # inlude urls from members.py
