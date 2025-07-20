# models/report.py
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class SavedReport(Base):
    __tablename__ = "SavedReports"
    
    ReportID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID", ondelete="CASCADE"), nullable=False)
    ReportName = Column(String(255), nullable=False)
    ReportType = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    ReportConfig = Column(Text)  # JSON configuration
    LastGenerated = Column(DateTime)
    CreatedAt = Column(DateTime, default=func.getdate())
    
    # Relationship với User (nếu có model User)
    user = relationship("User", back_populates="saved_reports")