"""
    This script contains endpoints for messaging.
    
    Gather messages for user id's / user names
    Log messages sent from clients and publish from Redis

"""
from datetime import datetime, timezone
from pydantic import BaseModel

# python dependencies
from fastapi import APIRouter, Depends, HTTPException
from pymongo.asynchronous.collection import AsyncCollection
from bson import ObjectId

# Project Mongo Dependencies
from ..mongodb.mongo import get_messages_db

# Project Postgres Dependencies

# Project Redis Dependencies

router = APIRouter(prefix="/messages", tags=["Messages"])

# Expected JSON structure for each endpoint
class CreateMessage(BaseModel):
    sender_id: int
    content: str

async def create_message_entry(sender_id: int, content: str, channel_name: str):
    msg_db = get_messages_db()
    msg_collection: AsyncCollection = msg_db.get_collection("messages")

    # TODO: validate if user exists within postgres db
    # TODO: implement redis pub sub validation

    msg_document = {
        "_id" : ObjectId(),
        "sender_id" : sender_id, # references PSQL users db
        "content" : content,
        "sent_at" : datetime.now(timezone.utc),
        "channel_id" : channel_name # temp, may add channels later so wanted support just in case
    }

    await msg_collection.insert_one(msg_document)

@router.get("/channel")
async def get_message_data():
    msg_db = get_messages_db()
    msg_collection: AsyncCollection = msg_db.get_collection("messages")

@router.get("/")
async def get_message_log():
    msg_db = get_messages_db()
    msg_collection: AsyncCollection = msg_db.get_collection("messages")

    documents_json = []

    async with msg_collection.find().sort('sent_at') as cursor:
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents_json.append(doc)
            
    return {"messages": documents_json}
    