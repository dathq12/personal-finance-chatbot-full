# budget.py
from sqlalchemy import Column, String, Date, Time, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
from datetime import datetime

class Budget(Base):
    __tablename__ = "Budgets"
    BudgetID = Column(UNIQUEIDENTIFIER, primary_key=True)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    CategoryID = Column(UNIQUEIDENTIFIER, ForeignKey("Categories.CategoryID"))
    BudgetName = Column(String(255), nullable=False)
    BudgetType = Column(String(20), nullable=False)
    Amount = Column(Numeric(15,2), nullable=False)
    PeriodStart = Column(Date, nullable=False)
    PeriodEnd = Column(Date, nullable=False)
    AlertThreshold = Column(Numeric(5,2), default=80.00)
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow)

class BudgetAlert(Base):
    __tablename__ = "BudgetAlerts"
    AlertID = Column(UNIQUEIDENTIFIER, primary_key=True)
    BudgetID = Column(UNIQUEIDENTIFIER, ForeignKey("Budgets.BudgetID"))
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"))
    AlertType = Column(String(20), nullable=False)
    CurrentAmount = Column(Numeric(15,2), nullable=False)
    BudgetAmount = Column(Numeric(15,2), nullable=False)
    PercentageUsed = Column(Numeric(5,2), nullable=False)
    Message = Column(String)
    IsRead = Column(Boolean, default=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
