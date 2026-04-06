from pymongo import AsyncMongoClient, ASCENDING, DESCENDING
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:mongo@mongodb:27017/?authSource=admin")
m_client = AsyncMongoClient(MONGO_URL)


def get_messages_db() -> AsyncDatabase:
    return m_client["chatdb"]

async def mongodb_init():
    try:
        await m_client.admin.command("ping")
        print("Connection to MongoDB was successful")

        # create collection within db if not exists
        mongo_chatdb = get_messages_db()

        msg_collection: AsyncCollection = mongo_chatdb.get_collection("messages")
        await msg_collection.create_index([
            ("sender_id", ASCENDING),
            ("sent_at", ASCENDING)
        ])
        
    except Exception as e:
        raise Exception("There was an error while connecting to MongoDB: ", e)