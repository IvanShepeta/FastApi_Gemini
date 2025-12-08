from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.database import Base

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))

    # relationship with ChatRequests
    chats = relationship("ChatRequest", back_populates="owner", cascade="all, delete-orphan")

class ChatRequest(Base):
    __tablename__ = "chat_requests"

    id = Column(Integer, primary_key=True, nullable=False)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))

    # relationship with User
    owner = relationship("User", back_populates="chats")

