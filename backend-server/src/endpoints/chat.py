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

# Project Mongo Dependencies
from ..mongodb.mongo import get_messages_db

# Project Postgres Dependencies
from sqlalchemy.orm import Session
from ..postgres_db.postgres_schemas import User
from ..postgres_db.postgres_utils import get_psql_db, get_user, create_user

from . import users

# Project Redis Dependencies
from redis.asyncio import Redis

SECRET = "woopswoopswoopswoops"
ENCRYPTION_ALG = "HS256"

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


# data strucutres
CHANNEL_IDS: list[str] = [
    "general",
    "gaming",
    "offtopic"
]

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
            await socket.send_json({"error_msg": "User not found"})
            await connection_manager.disconnect(socket)
            return
    except jwt.ExpiredSignatureError:
        await socket.send_json({"error_msg": "Expired token"})
        await connection_manager.disconnect(socket)
        return
    except jwt.InvalidTokenError:
        await socket.send_json({"error_msg": "Invalid token"})
        await connection_manager.disconnect(socket)
        return
    
    await socket.send_json({
        "status": "connected"
    })

    try: 
        publisher = redis_instance.pubsub()
        await publisher.subscribe("general")

        print("SUBSCRIBED TO:", publisher.channels)
        # for channel_id in CHANNEL_IDS:
        #     await publisher.subscribe(channel_id)
    except Exception as e:
        await socket.send_json({"error": "Internal Server Error"})
        await connection_manager.disconnect(socket)
        return;

    async def publisher_listener():
        async for msg in publisher.listen():
            print(msg)
            if msg["type"] == "message":
                await socket.send_text(msg["data"])
            

    task = asyncio.create_task(publisher_listener())
    
    try:
        while True:
            data = await socket.receive_json()
            data["sender_id"] = user_id

            channel_name = data.get("channel")
            if not channel_name:
                continue

            #todo: call message save function to save message to mongo, already implemented need to add here

            await redis_instance.publish(channel_name, json.dumps(data))
    except WebSocketDisconnect:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await publisher.close()