# models/budget_model.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, text, Unicode, DECIMAL, Date
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date
import uuid

class Budget(Base):
    __tablename__ = "Budgets"
    __table_args__ = {'extend_existing': True}
    
    BudgetID = Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("NEWID()")
    )
    UserID = Column(
        UNIQUEIDENTIFIER, 
        nullable=False,
        index=True
    )
    BudgetName = Column(Unicode(255), nullable=False)
    BudgetType = Column(Unicode(20), nullable=False)  # 'monthly', 'weekly', 'yearly'
    Amount = Column(DECIMAL(15, 2), nullable=False)
    
    PeriodStart = Column(Date, nullable=False)
    PeriodEnd = Column(Date, nullable=False)
    
    AutoAdjust = Column(Boolean, default=False, nullable=False)
    IncludeIncome = Column(Boolean, default=False, nullable=False)
    AlertThreshold = Column(DECIMAL(5, 2), default=80.00, nullable=False)
    IsActive = Column(Boolean, default=True, nullable=False, index=True)
    
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # budget_categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete-orphan")
    # budget_alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")

class BudgetAlert(Base):
    __tablename__ = "BudgetAlerts"
    __table_args__ = {'extend_existing': True}
    
    AlertID = Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("NEWID()")
    )
    BudgetID = Column(
        UNIQUEIDENTIFIER, 
        nullable=False,
        index=True
    )
    UserID = Column(
        UNIQUEIDENTIFIER, 
        nullable=False,
        index=True
    )
    AlertType = Column(Unicode(20), nullable=False)  # 'warning', 'exceeded', 'near_limit'
    CurrentAmount = Column(DECIMAL(15, 2), nullable=False)
    BudgetAmount = Column(DECIMAL(15, 2), nullable=False)
    PercentageUsed = Column(DECIMAL(5, 2), nullable=False)
    Message = Column(Unicode, nullable=True)
    IsRead = Column(Boolean, default=False, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # budget = relationship("Budget", back_populates="budget_alerts")

class BudgetCategory(Base):
    __tablename__ = "BudgetCategories"
    __table_args__ = {'extend_existing': True}
    
    BudgetCategoryID = Column(
        UNIQUEIDENTIFIER, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        server_default=text("NEWID()")
    )
    BudgetID = Column(
        UNIQUEIDENTIFIER, 
        nullable=False,
        index=True
    )
    UserCategoryID = Column(
        UNIQUEIDENTIFIER, 
        nullable=False,
        index=True
    )
    AllocatedAmount = Column(DECIMAL(15, 2), nullable=False)
    SpentAmount = Column(DECIMAL(15, 2), default=0, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # budget = relationship("Budget", back_populates="budget_categories")
    # user_category = relationship("UserCategory", back_populates="budget_categories")