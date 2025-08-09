# income.py
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from database import Base
from datetime import datetime, timezone
class ChatSession(Base):
    __tablename__ = "ChatSessions"
    SessionID = Column(UNIQUEIDENTIFIER, primary_key=True)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    SessionName = Column(String(255))
    StartedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    EndedAt = Column(DateTime)
    IsActive = Column(Boolean, default=True)
    MessageCount = Column(Integer, default=0)

class ChatMessage(Base):
    __tablename__ = "ChatMessages"
    MessageID = Column(UNIQUEIDENTIFIER, primary_key=True)
    SessionID = Column(UNIQUEIDENTIFIER, ForeignKey("ChatSessions.SessionID"))
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    MessageType = Column(String(20), nullable=False)
    Content = Column(String, nullable=False)
    Intent = Column(String(50))
    ActionTaken = Column(String(50))
    CreatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
