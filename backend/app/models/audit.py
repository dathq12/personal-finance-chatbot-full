from sqlalchemy import Column, String, Date, Time, Boolean, ForeignKey, Numeric, DateTime,text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class AuditLog(Base):
    __tablename__ = "AuditLogs"

    AuditLogID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("NEWID()"))
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID", ondelete="SET NULL"), nullable=True)
    TableName = Column(String(50), nullable=False)
    RecordID = Column(UNIQUEIDENTIFIER, nullable=False) # ID của bản ghi bị ảnh hưởng    
    Action = Column(String(20), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    OldValues = Column(String, nullable=True)  # JSON string of old values
    NewValues = Column(String, nullable=True)  # JSON string of new values  
    IPAddress = Column(String(45), nullable=True)  # IP address of the user
    CreatedAt = Column(DateTime, default=datetime, nullable=False)

    # User = relationship("User", back_populates="AuditLogs", uselist=False)  # Optional relationship