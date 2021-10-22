from fastapi import APIRouter, Response, status
from utils.db_handler import *
from schema.roomSchema import *


router = APIRouter()

@router.get("/org/{org_id}/users/{user_id}/rooms", status_code = status.HTTP_200_OK)
async def user_rooms(user_id: str, org_id: str, response: Response):
    """Get the rooms a user is in

    Args:
        user_id (str): The user id

    Returns:
        [List]: [description]
    """
    result = await get_rooms(user_id, org_id)

    if result:
        return result
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return result


