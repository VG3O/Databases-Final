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
from sqlalchemy.orm import Session
from ..postgres_db.postgres_schemas import User, TextChannel
from ..postgres_db.postgres_utils import get_psql_db, get_user, create_user

# Project Redis Dependencies

from .users import User

router = APIRouter(prefix="/messages", tags=["Messages"])

# Expected JSON structure for each endpoint
class CreateMessage(BaseModel):
    sender_id: int
    content: str


async def create_message_entry(sender_id: int, channel_id: int, content: str, usersdb: Session):
    """
        Take in input data and process the message into the Mongo database.
        Return a JSON table to publish to each client.
    """
    msg_db = get_messages_db()
    msg_collection: AsyncCollection = msg_db.get_collection("messages")

    msg_document = {
        "_id" : ObjectId(),
        "sender_id" : sender_id, # references PSQL users db
        "content" : content,
        "sent_at" : datetime.now(timezone.utc),
        "channel_id" : channel_id 
    }

    # insert the document to the messages db
    await msg_collection.insert_one(msg_document)

    # after insertion, convert non-json types to json-readable types
    msg_document["_id"] = str(msg_document["_id"])
    msg_document["sent_at"] = msg_document["sent_at"].strftime("%m/%d/%Y %I:%M %p")

    # get sender name so we can visually reflect who sent the message
    user = get_user(usersdb, msg_document["sender_id"])
    if user is None:
        msg_document["sender_name"] = "Unknown User"
    else:
        msg_document["sender_name"] = user.user_name 

    return msg_document

async def get_channel_messages(channel_id: int, usersdb: Session):
    msg_db = get_messages_db()
    msg_collection: AsyncCollection = msg_db.get_collection("messages")

    cursor = msg_collection.find({"channel_id": channel_id}).sort("sent_at", 1)

    msg_list = await cursor.to_list()

    # serialize so that json doesnt throw a fit
    for msg in msg_list:
        msg["_id"] = str(msg["_id"])
        msg["sent_at"] = msg["sent_at"].strftime("%m/%d/%Y %I:%M %p")

        # get sender name so we can visually reflect who sent the message
        user = get_user(usersdb, msg["sender_id"])
        if user is None:
            msg["sender_name"] = "Unknown User"
        elif user.deleted_at is None:
            msg["sender_name"] = user.user_name  
        else:
            msg["sender_name"] = "Deleted User"

    return msg_list

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
    