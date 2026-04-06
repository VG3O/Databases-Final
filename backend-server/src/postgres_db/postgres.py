from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/chatdb")

postgres_engine = create_engine(DATABASE_URL)
postgres_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)
postgres_Base = declarative_base()