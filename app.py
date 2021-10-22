from typing import Optional
from fastapi import FastAPI, status, Response
from utils.db_handler import *

app = FastAPI()


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