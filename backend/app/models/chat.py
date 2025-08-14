# models/chatbot.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Float, Text,UnicodeText
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class ChatSession(Base):
    __tablename__ = "ChatSessions"
    __table_args__ = {'extend_existing': True}

    SessionID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    UserID = Column(UNIQUEIDENTIFIER, nullable=False)
    SessionName = Column(String(255))
    StartedAt = Column(DateTime, default=datetime.utcnow)
    EndedAt = Column(DateTime)
    IsActive = Column(Boolean, default=True)
    MessageCount = Column(Integer, default=0)
    
    # Relationship to messages
    # messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "ChatMessages"
    __table_args__ = {'extend_existing': True}

    MessageID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    SessionID = Column(UNIQUEIDENTIFIER, nullable=False)
    UserID = Column(UNIQUEIDENTIFIER, nullable=False)
    MessageType = Column(String(20), nullable=False)  # 'user', 'bot', 'system'
    Content = Column(UnicodeText, nullable=False)
    Intent = Column(String(50))
    Entities = Column(Text)  # JSON string for storing extracted entities
    ConfidenceScore = Column(Float)
    ActionTaken = Column(String(50))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to session
    # session = relationship("ChatSession", back_populates="messages")