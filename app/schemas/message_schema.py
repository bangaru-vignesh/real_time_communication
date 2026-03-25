from pydantic import BaseModel, StrictStr
from datetime import datetime


class MessageCreate(BaseModel):
    sender_id: str
    receiver_id: str
    content: StrictStr

class MessageResponse(BaseModel):
    id: int
    sender_id: str
    receiver_id: str
    content: StrictStr
    status: str = "sent"
    timestamp: datetime

    class Config:
        from_attributes = True
