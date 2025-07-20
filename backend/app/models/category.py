# models/category_model.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class Category(Base):
    __tablename__ = "Categories"
    
    CategoryID = Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("NEWID()")
    )
    CategoryName = Column(String(100), nullable=False, index=True)
    CategoryType = Column(String(20), nullable=False, index=True)
    ParentCategoryID = Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("Categories.CategoryID", ondelete="SET NULL"),
        nullable=True
    )
    Description = Column(String(500), nullable=True)
    Icon = Column(String(50), nullable=True)
    Color = Column(String(7), nullable=True)  # Hex color code
    IsDefault = Column(Boolean, default=False, nullable=False)
    IsActive = Column(Boolean, default=True, nullable=False, index=True)
    SortOrder = Column(Integer, default=0, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    parent_category = relationship("Category", remote_side=[CategoryID], back_populates="children")
    children = relationship("Category", back_populates="parent_category", cascade="all, delete-orphan")
    user_categories = relationship("UserCategory", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(CategoryID={self.CategoryID}, CategoryName='{self.CategoryName}')>"

class UserCategory(Base):
    __tablename__ = "UserCategories"
    
    UserCategoryID = Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("NEWID()")
    )
    UserID = Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("Users.UserID", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    CategoryID = Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("Categories.CategoryID", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    CustomName = Column(String(100), nullable=True)
    IsActive = Column(Boolean, default=True, nullable=False, index=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="user_categories")
    # user = relationship("User", back_populates="user_categories")  # Uncomment if User model exists
    
    # Unique constraint for user-category combination
    __table_args__ = (
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<UserCategory(UserCategoryID={self.UserCategoryID}, UserID={self.UserID}, CategoryID={self.CategoryID})>"