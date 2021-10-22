from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Room(BaseModel):
    org_id : str
    bookmark : List[str] = []
    pinned : List[str] = []
    closed : bool = False
    private : bool = False
    room_name : Optional[str]
    room_user_ids : List[str] = []
    starred : List[str] = []
    created_at : datetime = datetime.now()

