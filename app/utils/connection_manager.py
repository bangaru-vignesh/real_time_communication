import json
import redis.asyncio as aioredis
from typing import Dict, List
from fastapi import WebSocket
from app.core.config import settings


class ConnectionManager:
    def __init__(self):
        # Multiple device support: Now stores a list of WebSockets per user
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Connect to Redis server from settings
        self.redis = aioredis.from_url(settings.REDIS_URL)
        self.pubsub = self.redis.pubsub()

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        
        is_new_online = False
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            is_new_online = True  # They were completely offline before this
            
        self.active_connections[user_id].append(websocket)

        # Broadcast online status strictly if they are logging in on their first device
        if is_new_online:
            await self.broadcast_to_redis({
                "type": "status",
                "user_id": user_id,
                "status": "online"
            })

    async def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            # Remove this specific device
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                
            # If they closed their LAST device, they are truly offline
            if len(self.active_connections[user_id]) == 0:
                self.active_connections.pop(user_id, None)
                await self.broadcast_to_redis({
                    "type": "status",
                    "user_id": user_id,
                    "status": "offline"
                })

    def is_online_local(self, user_id: str) -> bool:
        """Check if user is locally connected."""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0

    async def broadcast_to_redis(self, message: dict):
        """Send a message to Redis so ALL servers can hear it."""
        await self.redis.publish("chat_channel", json.dumps(message))

    async def _redis_listener(self):
        """Background task that listens to Redis for messages routed to ANY user."""
        await self.pubsub.subscribe("chat_channel")
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"].decode("utf-8"))
                
                payload_type = data.get("type")
                
                if payload_type == "status":
                    # Forward "online"/"offline" to ALL active websockets globally
                    for ws_list in self.active_connections.values():
                        for ws in ws_list:
                            try:
                                await ws.send_json(data)
                            except Exception:
                                pass
                else:
                    # Specific receiver (message, typing, seen, etc.)
                    receiver = data.get("receiver_id")
                    if receiver and self.is_online_local(receiver):
                        # Send to ALL devices this specific user owns locally
                        dead_sockets = []
                        for ws in self.active_connections[receiver]:
                            try:
                                await ws.send_json(data)
                            except Exception:
                                dead_sockets.append(ws)
                        
                        # Cleanup any broken pipelines we discovered
                        for ws in dead_sockets:
                            await self.disconnect(receiver, ws)
