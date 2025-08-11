# models/budget_model.py
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

class Budget(Base):
    __tablename__ = "Budgets"
    __table_args__ = {'extend_existing': True}

   # Primary key
    BudgetID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    UserID = Column(UNIQUEIDENTIFIER, nullable=False)
    
    # Budget details - mapped từ Pydantic schema
    BudgetName = Column(String(255), nullable=False)  # budget_name
    BudgetType = Column(String(20), nullable=False)   # budget_type: monthly, weekly, yearly
    Amount = Column(Numeric(15,2), nullable=False)    # amount
    
    # Period information
    PeriodStart = Column(Date, nullable=False)        # period_start
    PeriodEnd = Column(Date, nullable=False)          # period_end
    
    # Calculated and configuration fields
    TotalSpent = Column(Numeric(15,2), default=0)     # total_spent (calculated)
    AutoAdjust = Column(Boolean, default=False)       # auto_adjust
    AlertThreshold = Column(Numeric(5,2), default=80.0)  # alert_threshold
    IsActive = Column(Boolean, default=True)          # is_active
    
    # Timestamps
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (optional)
    # categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete")
    # alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete")

class BudgetCategory(Base):
    __tablename__ = "BudgetCategories"
    __table_args__ = {'extend_existing': True}

    # Primary key
    BudgetCategoryID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    BudgetID = Column(UNIQUEIDENTIFIER, nullable=False)
    UserCategoryID = Column(UNIQUEIDENTIFIER, nullable=False)
    
    # Amount fields - mapped từ Pydantic schema
    AllocatedAmount = Column(Numeric(15,2), nullable=False)  # allocated_amount
    SpentAmount = Column(Numeric(15,2), default=0)           # spent_amount (calculated)
    
    # Timestamps
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # budget = relationship("Budget", back_populates="categories")
    # alerts = relationship("BudgetAlert", back_populates="budget_category", cascade="all, delete-orphan")

class BudgetAlert(Base):
    __tablename__ = "BudgetAlerts"
    __table_args__ = {'extend_existing': True}
# Primary key
    AlertID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    BudgetID = Column(UNIQUEIDENTIFIER,  nullable=False)
    BudgetCategoryID = Column(UNIQUEIDENTIFIER,  nullable=True)
    UserID = Column(UNIQUEIDENTIFIER,  nullable=False)
    
    # Alert details - mapped từ Pydantic schema
    AlertType = Column(String(20), nullable=False)        # alert_type
    CurrentAmount = Column(Numeric(15,2), nullable=False) # current_amount
    PercentageUsed = Column(Numeric(5,2), nullable=False) # percentage_used
    Message = Column(Text, nullable=True)                 # message
    IsRead = Column(Boolean, default=False)               # is_read
    
    # Timestamp
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships (optional)
    # budget = relationship("Budget", back_populates="alerts")