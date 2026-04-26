from sqlalchemy import Column, Integer, String, DateTime
from .postgres import postgres_Base

class User(postgres_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(30), index=True, unique=True)
    password = Column(String(30), index=True)
    email = Column(String(40), index=True, unique=True)
    created_at = Column(DateTime, index=True)
    deleted_at = Column(DateTime, nullable=True)