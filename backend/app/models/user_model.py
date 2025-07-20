# from sqlalchemy import Column, Integer, String
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, index=True)
#     password_hash = Column(String)

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base  # hoặc từ .base import Base nếu dùng cấu trúc riêng
import uuid

class User(Base):
    __tablename__ = "Users"

    UserID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("NEWID()"))
    Email = Column(String(255), unique=True, nullable=False)
    PasswordHash = Column(String(255), nullable=False)
    FullName = Column(String(255), nullable=False)
    Phone = Column(String(20))
    AvatarURL = Column(String(500))
    TimeZone = Column(String(50), server_default=text("'SE Asia Standard Time'"))
    Currency = Column(String(3), server_default=text("'VND'"))
    IsActive = Column(Boolean, server_default=text("1"))
    EmailVerified = Column(Boolean, server_default=text("0"))
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))
    UpdatedAt = Column(DateTime, server_default=text("GETDATE()"))
    LastLogin = Column(DateTime)

    Sessions = relationship("UserSession", back_populates="User", cascade="all, delete")


class UserSession(Base):
    __tablename__ = "UserSessions"

    SessionID = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text("NEWID()"))
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID", ondelete="CASCADE"), nullable=False)
    RefreshToken = Column(String(500), nullable=False)
    DeviceInfo = Column(String)  # NVARCHAR(MAX) ánh xạ thành String
    IPAddress = Column(String(45))
    ExpiresAt = Column(DateTime, nullable=False)
    CreatedAt = Column(DateTime, server_default=text("GETDATE()"))

    User = relationship("User", back_populates="Sessions")
