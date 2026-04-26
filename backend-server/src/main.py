# Main dependencies
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Postgres Dependencies
from .postgres_db.postgres import postgres_engine
from .postgres_db.postgres_schemas import postgres_Base
# from .postgres_db.postgres_utils import run_psql_script

# Mongo Dependencies
from .mongodb.mongo import mongodb_init

# Redis Dependencies
from redis.asyncio import Redis

# Endpoints
from .endpoints import users, messages, chat

# Init API & run startup scripts

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb_init() # asynchronously initialize mongo

    chat.redis_instance = Redis(host='redis', port=6379, decode_responses=True)

    yield # anything above this is a startup event, anything below it is a shutdown event
    await chat.redis_instance.close()


app = FastAPI(title="Chat App Backend", lifespan=lifespan)

# init users DB utilizing PostgreSQL
postgres_Base.metadata.create_all(bind=postgres_engine)

# router attachment
app.include_router(users.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(chat.router, prefix="/api")