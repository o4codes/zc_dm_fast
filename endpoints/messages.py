from starlette import status
from starlette.exceptions import HTTPException
from utils.db_handler import *
from utils.centrifugo_handler import centrifugo_client
from fastapi import APIRouter
from fastapi import status
from schema import messageSchema

router = APIRouter()

@router.delete("/messages", status_code=status.HTTP_200_OK)
async def delete_message(message_id, room_id):
    """
    This function deletes message in rooms using message
    organization id (org_id), room id (room_id) and the message id (message_id).
    """
    try:
        message = DB.read("dm_messages", {"_id": message_id})
        room = DB.read("dm_rooms", {"_id": room_id})

        if room and message:
            response = DB.delete("dm_messages", message_id)
            if response.get("status") == 200:
                response_output = {
                    "status": response["message"],
                    "event": "message_delete",
                    "room_id": room_id,
                    "message_id": message_id,
                }
                centrifugo_data = centrifugo_client.publish(room=room_id, data=response)
                if centrifugo_data and centrifugo_data.get("status_code") == 200:
                        return {"data": response_output}

                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                        detail="Message not sent")    
                    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Message not found")         
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e))


@router.post("/org/{org_id}/rooms/{room_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_message(org_id:str, room_id:str, message:messageSchema.Message):
    db_handler = DataStorage()
    db_handler.organization_id = org_id
    
    message = message.dict() # convert obj to dictionary
    
    room_id = message["room_id"]  # room id gotten from client request

    room =  await DB.read_query("dm_rooms", query={"_id": room_id})
    if room and room.get("status_code", None) == None:
        if message["sender_id"] in room.get("room_user_ids", []):

            response = DB.write("dm_messages", message)
            if response.get("status", None) == 200:

                response_output = {
                    "status": response["message"],
                    "event": "message_create",
                    "message_id": response["data"]["object_id"],
                    "room_id": room_id,
                    "thread": False,
                    "data": {
                        "sender_id": message["sender_id"],
                        "message": message["message"],
                        "created_at": message["created_at"],
                    },
                }
                try:
                    centrifugo_data = centrifugo_client.publish(
                        room=room_id, data=response_output
                    )  # publish data to centrifugo
                    if (
                        centrifugo_data
                        and centrifugo_data.get("status_code") == 200
                    ):

                            return response_output

                    else:
                        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, 
                                            detail="message not sent")
                except:
                    raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                        detail="centrifugo server not available")
            
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, 
                                detail="message not saved and not sent")
                   
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender not in room") 
       
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="room not found")
