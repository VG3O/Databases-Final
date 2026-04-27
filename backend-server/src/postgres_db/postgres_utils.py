# This script contains useful utility functions for interfacing with the 'chatdb' PostgreSQL database

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from .postgres_schemas import User
from .postgres import postgres_SessionLocal, postgres_engine

import re

EMAIL_PATTERN = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

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

def create_user(db: Session, user_name: str, email: str, password: str):
    db_user = User(user_name=user_name, email=email, password=password)
    db_user.created_at = datetime.now(timezone.utc)
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        
        err_msg = str(e.orig)

        if "users_user_name_key" in err_msg:
            raise HTTPException(400, "Username is taken")
        elif "users_email_key" in err_msg:
            raise HTTPException(400, "Email is already in use")
        
        # no conflict found
        raise HTTPException(500, "Internal Database Error")
