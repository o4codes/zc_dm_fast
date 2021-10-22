from typing import List, Optional
from pydantic import BaseModel, AnyUrl
from pydantic.fields import Field
from starlette import status
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
    id: Optional[str] = Field(..., alias='_id')
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

class MessageError(BaseModel):
    message: str

class ReadStatus(BaseModel):
    read: bool

class MessageUpdateIn(BaseModel):
    sender_id: str
    room_id: str
    message_id: str
    message: str

class MessageUpdateOut(BaseModel):
    status: str
    sender_id: str
    room_id: str
    message_id: str
    message: str
    event: str