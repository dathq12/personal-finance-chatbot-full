from sqlalchemy import Column, String, Date, Time, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "AuditLogs"
    AuditID = Column(UNIQUEIDENTIFIER, primary_key=True)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    TableName = Column(String(50), nullable=False)
    RecordID = Column(UNIQUEIDENTIFIER, nullable=False)
    Action = Column(String(20), nullable=False)
    OldValues = Column(String)
    NewValues = Column(String)
    IPAddress = Column(String(45))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
