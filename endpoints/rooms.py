from fastapi import FastAPI, Response, status
from utils.db_handler import *

app = FastAPI()

@app.get("/{org_id}/rooms/{user_id}", status_code = 200)
async def get_rooms(user_id: str, org_id: str, response: Response):
    """Get the rooms a user is in

    Args:
        user_id (str): The user id

    Returns:
        [List]: [description]
    """

    helper = DataStorage()
    helper.organization_id = org_id
    query = {"room_user_ids":user_id}
    options = {"sort":{"created_at":-1}}
    response = helper.read_query("dm_rooms", query=query, options=options)

    if response and "status_code" not in response:
        return response
    response.status_code = status.HTTP_204_NO_CONTENT
    return []
from fastapi import  APIRouter
router = APIRouter()
