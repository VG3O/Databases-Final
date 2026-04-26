"""
    This script contains all endpoints pertaining to user managment.

    Users can be created, deleted, updated, as well as performing Redis subscribing on User login.
"""

# Main dependencies
from datetime import datetime, timezone
from typing import List, Dict
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

# Postgres Dependencies
from ..postgres_db.postgres import postgres_engine, postgres_SessionLocal
from ..postgres_db.postgres_schemas import postgres_Base, User
from ..postgres_db.postgres_utils import get_psql_db, get_user, create_user

# Init API & routers for each enpoint
router = APIRouter(prefix="/users", tags=["Users"])

# Expected JSON structure for each endpoint
class CreateUser(BaseModel):
    username: str
    email: str

# Utilities
def auth_user(username: str, password: str, db: Session):
    user_obj = db.query(User).filter(User.user_name == username).first()
    if user_obj is None: 
        return None; # not found user

    if user_obj.password == password:
        return user_obj
    else:
        return -1 # wrong password

def does_user_exist(id: int, db: Session):
    user_obj = db.query(User).filter(User.id == id).first()
    if not user_obj:
        return False
    return True

# Endpoints
@router.post("/")
async def create_user_endpoint(user: CreateUser, db: Session = Depends(get_psql_db)):
    print(user)
    return create_user(db, user.username, user.email)

@router.get("/{user_id}")
async def get_user_endpoint(user_id: int, db: Session = Depends(get_psql_db)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_psql_db)):
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif user.deleted_at is not None:
        raise HTTPException(status_code=403, detail="This user is already deleted.")
    
    # soft delete user if found
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return {"detail": "User " + str(user_id) + " deleted."}

@router.get("/")
async def get_user_data(db: Session = Depends(get_psql_db)):
    totalUsers = db.query(func.count(User.id)).scalar()
    activeUsers = db.query(func.count(User.id)).filter(User.deleted_at.is_(None)).scalar()
    userData = db.query(User).all()

    returnJson = {
        "userData": userData,
        "totalRegistered": totalUsers,
        "activeUsers": activeUsers
    }
    return returnJson