from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # hoặc từ .base import Base nếu dùng cấu trúc riêng
import uuid

class User(Base):
    __tablename__ = "Users"
    __table_args__ = {'extend_existing': True}
    UserID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("NEWID()"))
    email = Column("Email",String(255), unique=True, nullable=False)
    password_hash = Column("PasswordHash",String(255), nullable=False)
    FullName = Column(String(255), nullable=False)
    Phone = Column(String(20))
    Currency = Column(String(3), server_default=text("'VND'"))
    IsActive = Column(Boolean, server_default=text("1"))
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))
    UpdatedAt = Column(DateTime, server_default=text("GETDATE()"))
    LastLogin = Column(DateTime)

    # Sessions = relationship("UserSession", back_populates="User", cascade="all, delete")


class UserSession(Base):
    __tablename__ = "UserSessions"
    __table_args__ = {'extend_existing': True}
    SessionID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("NEWID()"))
    UserID = Column(UNIQUEIDENTIFIER, nullable=False)
    RefreshToken = Column(String(500), nullable=False)
    DeviceInfo = Column(String)  # NVARCHAR(MAX) ánh xạ thành String
    IPAddress = Column(String(45))
    ExpiresAt = Column(DateTime, nullable=False)
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))

    # User = relationship("User", back_populates="Sessions")


