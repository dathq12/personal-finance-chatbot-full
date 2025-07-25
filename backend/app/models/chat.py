# income.py
from sqlalchemy import Column, String, Date, Time, Boolean, ForeignKey, Numeric, DateTime,Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from database import Base
from datetime import datetime
class ChatSession(Base):
    __tablename__ = "ChatSessions"
    SessionID = Column(UNIQUEIDENTIFIER, primary_key=True)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    SessionName = Column(String(255))
    StartedAt = Column(DateTime, default=datetime.utcnow)
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
    CreatedAt = Column(DateTime, default=datetime.utcnow)

# thêm ChatbotTrainingData (25/7/25 Sơn)
class ChatbotTrainingData(Base):
    __tablename__ = "chatbot_training_data"
    id = Column("TrainingID", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column("UserID", String, ForeignKey("users.UserID"), nullable=False)
    question = Column("Question", Text, nullable=False)
    intent = Column("Intent", String(50), nullable=False)
    entities = Column("Entities", Text)
    confidence_score = Column("ConfidenceScore", Float)
    timestamp = Column("Timestamp", DateTime, default=datetime.utcnow)
