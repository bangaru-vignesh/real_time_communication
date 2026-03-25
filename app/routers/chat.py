from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List

from app.utils.connection_manager import ConnectionManager
from app.core.database import SessionLocal
from app.models.message import Message
from app.schemas.message_schema import MessageResponse

router = APIRouter()

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    db = SessionLocal()
    try:
        while True:
            data = await websocket.receive_json()
            
            # Distinguish the type of message coming from the frontend
            event_type = data.get("type", "chat")
            receiver = data.get("receiver")
            
            if event_type == "chat":
                content = data.get("content", "")
                
                # Save to Database with default status
                new_message = Message(sender_id=user_id, receiver_id=receiver, content=content, status="sent")
                db.add(new_message)
                db.commit()
                db.refresh(new_message)
                
                msg_data = {
                    "type": "message",  # Standard message
                    "id": new_message.id,
                    "sender_id": user_id,
                    "receiver_id": receiver,
                    "content": content,
                    "status": "sent",
                    "timestamp": str(new_message.timestamp)
                }
                # Publish event to Redis instead of sending locally
                await manager.broadcast_to_redis(msg_data)
                
            elif event_type in ["typing", "delivered", "seen"]:
                # If it is a read receipt, update the DB
                if event_type in ["delivered", "seen"] and "message_id" in data:
                    msg_to_update = db.query(Message).filter(Message.id == data["message_id"]).first()
                    if msg_to_update:
                        msg_to_update.status = event_type
                        db.commit()
                
                # Route control message
                payload = {
                    "type": "message",
                    "event_action": event_type, 
                    "sender_id": user_id,
                    "receiver_id": receiver
                }
                if "message_id" in data:
                    payload["message_id"] = data["message_id"]
                    
                await manager.broadcast_to_redis(payload)

    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    finally:
        db.close()


@router.get("/messages/{user1}/{user2}", response_model=List[MessageResponse])
def get_chat_history(user1: str, user2: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == user1, Message.receiver_id == user2),
            and_(Message.sender_id == user2, Message.receiver_id == user1)
        )
    ).order_by(Message.timestamp.asc()).all()
    return messages
