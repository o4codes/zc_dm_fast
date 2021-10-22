from fastapi import FastAPI, status, HTTPException, Request
from utils.db_handler import *
from utils.centrifugo_handler import centrifugo_client
from utils.decorators import db_init_with_credentials

from endpoints import messages

app = FastAPI()
app.include_router(messages.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# @app.get("/api/v1")
# async def read_root():
#     return {"Hello": "API"}


# @app.delete(
#     "api/v1/org/{org_id}/rooms/{room_id}/messages/{message_id}/messages",
#     status_code=status.HTTP_200_OK,
# )


# @app.get(
#     "/api/v1/un/org/{org_id}/rooms/{room_id}/messages/{message_id}",
#     status_code=status.HTTP_200_OK,
# )
# @db_init_with_credentials
# def delete_message(request: Request, room_id, message_id):
#     """
#     This function deletes message in rooms using message
#     organization id (org_id), room id (room_id) and the message id (message_id).
#     """
#     return {"data": "ok"}
#     try:
#         message = DB.read("dm_messages", {"_id": message_id})
#         room = DB.read("dm_rooms", {"_id": room_id})

#         if room and message:
#             response = DB.delete("dm_messages", message_id)
#             if response.get("status") == 200:
#                 response_output = {
#                     "status": response["message"],
#                     "event": "message_delete",
#                     "room_id": room_id,
#                     "message_id": message_id,
#                 }
#                 centrifugo_data = centrifugo_client.publish(room=room_id, data=response)
#                 if centrifugo_data and centrifugo_data.get("status_code") == 200:
#                     return {"data": response_output}

#                 raise HTTPException(
#                     status_code=status.HTTP_424_FAILED_DEPENDENCY,
#                     detail="Message not sent",
#                 )

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
