from typing import List
from pydantic import BaseModel, AnyUrl
from .threadSchema import Thread
from datetime import datetime, timezone

class Emoji(BaseModel):
    message_id : str
    sender_id : str
    data : str
    category : str
    aliases : List[str] = []
    count : int = 0
    created_at : str = str(datetime.now())

class Message(BaseModel):
    sender_id : str
    room_id : str = None
    message : str
    media : List[AnyUrl] = []
    read : bool = False
    pinned : bool = False
    saved_by : List[str] = []
    threads : List[Thread] = []
    replied_message : List = []
    reactions : List[Emoji] = []
    sent_from_thread : bool = False
    created_at : str = str(datetime.now())
