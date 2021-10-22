from starlette import status
from starlette.exceptions import HTTPException
import app
from utils.db_handler import *
from utils.centrifugo_handler import centrifugo_client


@app.delete("/messages", status_code=status.HTTP_200_OK)
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
                centrifugo_data = centrifugo_client.publish(
                        room=room_id, data=response
                    )
                if centrifugo_data and centrifugo_data.get("status_code") == 200:
                        return {"data": response_output)

                raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                        detail="Message not sent")    
                    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Message not found")         )
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e))
