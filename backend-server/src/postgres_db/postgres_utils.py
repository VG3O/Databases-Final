# This script contains useful utility functions for interfacing with the 'chatdb' PostgreSQL database

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .postgres_schemas import User
from .postgres import postgres_SessionLocal, postgres_engine

# Postgres general utility
""" Get the current PostgreSQL session. """
def get_psql_db():
    db = postgres_SessionLocal()
    try: 
        yield db
    finally:
        db.close()

def run_psql_script(path: str):
    print(path)

# 'User' utility
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_name: str, email: str):
    db_user = User(user_name=user_name, email=email)
    db_user.created_at = datetime.now(timezone.utc)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

