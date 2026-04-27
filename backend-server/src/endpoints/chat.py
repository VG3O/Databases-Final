"""
    This script contains endpoints for chat server handling.
    
    Manage client connections to the server, Redis pub subs, and replication

"""
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

# python dependencies
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pymongo.asynchronous.collection import AsyncCollection
from typing import Optional
from bson import ObjectId
import json
import jwt
import asyncio
import logging
import sys

# Project Mongo Dependencies

# Project Postgres Dependencies
from sqlalchemy.orm import Session
from ..postgres_db.postgres_schemas import User, TextChannel
from ..postgres_db.postgres_utils import get_psql_db, get_user, create_user

from . import users, messages

# Project Redis Dependencies
from redis.asyncio import Redis

SECRET = "woopswoopswoopswoops"
ENCRYPTION_ALG = "HS256"

# debug
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

redis_instance: Redis = None # we init this in main.py
router = APIRouter(prefix="/chat")

class ConnectionManager:
    def __init__(self):
        self.connected_clients: list[WebSocket] = []
    
    async def connect(self, socket: WebSocket):
        await socket.accept()
        self.connected_clients.append(socket)

    async def disconnect(self, socket: WebSocket):
        self.connected_clients.remove(socket)
        await socket.close()
    
    async def broadcast_to_channel(self):
        for connection in self.connected_clients:
            await connection


# data strucutres & utils
def get_channels(db: Session):
    return db.query(TextChannel).all()

def get_channel(id: int, db: Session):
    return db.query(TextChannel).filter(TextChannel.id == id).first()

class RequestLogin(BaseModel):
    username: str
    password: str

class LoginRequestResponse(BaseModel):
    status: str
    token: Optional[str] = None
    user_id: Optional[int] = None

connection_manager = ConnectionManager()

@router.post("/login")
async def check_credentials(request: RequestLogin, db: Session = Depends(get_psql_db)):
    user: User = users.auth_user(request.username, request.password, db=db)
    
    if not user:
        return LoginRequestResponse(
            status="Invalid username"
        )
    elif user == -1:
        return LoginRequestResponse(
            status="Incorrect password"
        )
    else: # user was matched correctly
        token = jwt.encode({ "user_id": user.id, "exp": datetime.now(timezone.utc) + timedelta(days=1) }, SECRET, algorithm=ENCRYPTION_ALG)
        
        return LoginRequestResponse(
            status="Success",
            token=token,
            user_id=user.id
        )
    
@router.websocket("/ws")
async def user_login_endpoint(socket: WebSocket, db: Session = Depends(get_psql_db)): # note if this password was deployed live it would be encoded in SHA512 hash
    await connection_manager.connect(socket)

    user_id = -1

    # decrypt auth token
    try:
        msg = await socket.receive_text()
        auth_data = json.loads(msg)
        auth_token = auth_data.get("token")

        data = jwt.decode(auth_token, SECRET, algorithms=[ENCRYPTION_ALG])

        user_id = data.get("user_id")

        if not users.does_user_exist(user_id, db=db):
            logger.warning(f"Disconnecting, user id was not found in DB (ID: {user_id})")
            await socket.send_json({"type": "error","error_msg": "User not found"})
            await connection_manager.disconnect(socket)
            return
    except jwt.ExpiredSignatureError:
        logger.warning(f"Disconnecting, token expired.")
        await socket.send_json({"type": "error","error_msg": "Expired token"})
        await connection_manager.disconnect(socket)
        return
    except jwt.InvalidTokenError:
        logger.warning(f"Disconnecting, invalid token.")
        await socket.send_json({"type": "error","error_msg": "Invalid token"})
        await connection_manager.disconnect(socket)
        return

    # pubsub subscriptions
    try: 
        publisher = redis_instance.pubsub()
        channels = [channel for channel in get_channels(db=db)]
        channel_names = [channel.name for channel in channels]
        await socket.send_json({
            "type": "update_channels", 
            "channels": [
                            {
                                "id": channel.id,
                                "name": channel.name
                            }
                            for channel in channels
                        ]});
        await publisher.subscribe(*channel_names)

        # send message history to client, default to first channel in db
        channel_messages = await messages.get_channel_messages(1, usersdb=db)
        await socket.send_json({
                    "type": "history",
                    "messages": channel_messages
                })

        logger.debug("SUBSCRIBED TO:", publisher.channels)
    except Exception as e:
        logger.error(f"Internal Server Error: {e}.")
        await socket.send_json({"type": "error","error_msg": "Internal Server Error"})
        await connection_manager.disconnect(socket)
        return;

    async def publisher_listener():
        async for msg in publisher.listen():
            logger.debug(f"REDIS RECV: {msg}")
            if msg["type"] == "message":
                await socket.send_text(msg["data"])
            

    task = asyncio.create_task(publisher_listener())
    
    try:
        while True:
            data = await socket.receive_json()
            logger.debug(f"Incoming message: {data}")
            message_type = data.get("type")

            # determine message type
            if message_type == "post":
                channel_id = data.get("channel")
                if not channel_id: 
                    continue

                channel = get_channel(channel_id, db=db)

                message_data = await messages.create_message_entry(
                    sender_id=user_id, 
                    channel_id=channel_id,
                    content=data["content"],
                    usersdb=db
                )
                message_data["type"] = "publish"
                logger.debug(channel.name)
                await redis_instance.publish(channel.name, json.dumps(message_data))
            elif message_type == "history":
                channel_id= data.get("channel")
                if not channel_id: 
                    continue
                
                channel = get_channel(channel_id, db=db)
                if channel is None:
                    continue

                # get messages from channel
                channel_messages = await messages.get_channel_messages(channel_id, usersdb=db)
                
                await socket.send_json({
                    "type": "history",
                    "messages": channel_messages
                })
    except WebSocketDisconnect:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await publisher.close()