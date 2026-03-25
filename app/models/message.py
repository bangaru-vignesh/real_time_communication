from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, index=True)
    receiver_id = Column(String, index=True)
    content = Column(String)
    status = Column(String, default="sent")  # sent, delivered, seen
    timestamp = Column(DateTime, default=datetime.utcnow)
