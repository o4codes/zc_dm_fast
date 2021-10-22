from fastapi import APIRouter, status
from starlette.responses import JSONResponse
from utils.db_handler import *
from schema.roomSchema import *
from utils.centrifugo_handler import centrifugo_client
from fastapi.responses import Response, JSONResponse



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


@router.post("/org/{org_id}/users/{member_id}/rooms")
async def create_room(org_id,member_id:str, room:Room):
    """
    Creates a room between users.
    It takes the id of the users involved, sends a write request to the database .
    Then returns the room id when a room is successfully created
    """
    
    room_dict = room.dict()
    room_user_ids = room_dict["room_user_ids"]
    
    db_handler = DataStorage()
    db_handler.organization_id = org_id

    if len(room_user_ids) > 2:
        # print("            --------MUKHTAR-------              \n\r")
        response = await group_room(org_id, member_id, room)
        if response.get('get_group_data'):
            return JSONResponse(content={"room_id" : response['room_id']}, status_code=response['status_code'])
    
    else:
        # print("            --------FAE-------              \n\r")
        user_rooms = await get_rooms(room_user_ids[0], org_id)
        if isinstance(user_rooms, list):
            for room in user_rooms:
                room_users = room["room_user_ids"]
                if set(room_users) == set(room_user_ids):  
                    return JSONResponse(content={"room_id": room["_id"]}, status_code=status.HTTP_200_OK)

        elif user_rooms is None:
            return JSONResponse(content="unable to read database", status=status.HTTP_424_FAILED_DEPENDENCY)

        elif user_rooms.get("status_code") != 404 or user_rooms.get("status_code") != 200:
            return JSONResponse(content="unable to read database", status_code=status.HTTP_424_FAILED_DEPENDENCY)
    
        fields = {"org_id": room_dict["org_id"],
                    "room_user_ids": room_dict["room_user_ids"],
                    "room_name": room_dict["room_name"],
                    "private": room_dict["private"],
                    "created_at": room_dict["created_at"],
                    "bookmark": [],
                    "pinned": [],
                    "starred": [],
                    "closed": False
                        }

        response = await db_handler.write("dm_rooms", data=fields)
        # ===============================

    if response.get("status") == 200:
        room_id = response.get("data").get("object_id")
        response_output = await sidebar_emitter(org_id=DB.organization_id, member_id=member_id, 
                                                group_room_name=room_dict["room_name"])

        try:
            centrifugo_data = centrifugo_client.publish(
                room=f"{org_id}_{member_id}_sidebar",
                data=response_output,
            )  # publish data to centrifugo
            if centrifugo_data and centrifugo_data.get("status_code") == 200:
                return JSONResponse(
                    content={"room_id":room_id,"message":"success"}, 
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return JSONResponse(
                    content="room created but centrifugo failed",
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                )
        except:
            return JSONResponse(
                content="centrifugo server not available",
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
            )
    return JSONResponse(content=f"unable to create room. Reason: {response}", 
                        status_code=status.HTTP_424_FAILED_DEPENDENCY)



async def group_room(org_id:str, member_id:str, room:Room):
    room_dict = room.dict()
    user_ids = room_dict["room_member_ids"]
    db_handler = DataStorage()
    db_handler.organization_id = org_id
    
    if len(user_ids) > 9:
        response = {
            "get_group_data": True,
            "status_code": 400,
            "room_id": "Group cannot have over 9 total users"
        }
        return response
    else:
        all_rooms = await db_handler.read("dm_rooms")
        if all_rooms and isinstance(all_rooms, list):
            for room_obj in all_rooms:
                try:
                    room_members = room_obj['room_user_ids']
                    if len(room_members) > 2 and set(room_members) == set(user_ids):
                        response = {
                            "get_group_data": True,
                            "status_code": 200,
                            "room_id": room_obj["_id"]
                        }
                        return response
                except KeyError:
                    pass

        fields = {
            "org_id": room_dict["org_id"],
            "room_user_ids": room_dict["room_member_ids"],
            "room_name": room_dict["room_name"],
            "private": room_dict["private"],
            "created_at": room_dict["created_at"],
            "bookmark": [],
            "pinned": [],
            "starred": [],
            "closed": False
        }
        response = await db_handler.write("dm_rooms", data=fields)

    return response


@router.get("/sidebar", status_code=status.HTTP_200_OK)
async def side_bar(org:str = None, user:str = None):
    org_id = org
    user_id = user
    
    db_handler = DataStorage()
    db_handler.organization_id = org_id
    
    rooms = []
    starred_rooms = []
    
    user_rooms = await get_rooms(user_id, org_id)
    members = await get_all_organization_members(org_id)
    
    if user_rooms != None:
        for room in user_rooms:
            room_profile = {}
            if len(room['room_user_ids']) == 2:
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"
                user_id_set = set(room['room_user_ids']).difference({user_id})
                partner_id = list(user_id_set)[0]              
                
                profile = await get_member(members,partner_id)

                if "user_name" in profile and profile['user_name'] != "":
                    if profile["user_name"]:
                        room_profile["room_name"] = profile["user_name"]
                    else:
                        room_profile["room_name"] = "no user name"
                    if profile["image_url"]:
                        room_profile["room_image"] = profile["image_url"]
                    else:
                        room_profile[
                            "room_image"
                        ] = "https://cdn.iconscout.com/icon/free/png-256/account-avatar-profile-human-man-user-30448.png"
                    
                else:
                    room_profile["room_name"] = "no user name"
                    room_profile[
                        "room_image"
                    ] = "https://cdn.iconscout.com/icon/free/png-256/account-avatar-profile-human-man-user-30448.png"
            else:
                room_profile["room_name"] = room["room_name"]
                room_profile["room_id"] = room["_id"]
                room_profile["room_url"] = f"/dm/{room['_id']}"
                room_profile[
                        "room_image"
                    ] = "https://cdn.iconscout.com/icon/free/png-256/account-avatar-profile-human-man-user-30448.png"

            rooms.append(room_profile)
            if user_id in room["starred"]:
                starred_rooms.append(room_profile)

    side_bar = {
        "name": "DM Plugin",
        "description": "Sends messages between users",
        "plugin_id": "dm.zuri.chat",
        "organisation_id": f"{org_id}",
        "user_id": f"{user_id}",
        "group_name": "DM",
        "category": "direct messages",
        "show_group": False,
        "button_url": f"/dm",
        "public_rooms": [],
        "starred_rooms": starred_rooms,
        "joined_rooms": rooms,
        # List of rooms/collections created whenever a user starts a DM chat with another user
        # This is what will be displayed by Zuri Main
    }
    return JSONResponse(content = side_bar, status_code=status.HTTP_200_OK)