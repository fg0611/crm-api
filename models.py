# models.py
from sqlalchemy import Column, DateTime, String, Boolean, Text
from .database import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    is_active = Column(Boolean, default=True)
    origin = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    conversation_state = Column(JSONB)
    current_step = Column(String)
    collected_data = Column(JSONB)
    previous_step = Column(String)
    name = Column(Text)