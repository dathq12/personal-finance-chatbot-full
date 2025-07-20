# transaction_model.py
from sqlalchemy import Column, String, Date, Time, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "Transactions"
    
    TransactionID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    UserID = Column(UNIQUEIDENTIFIER, ForeignKey("Users.UserID"), nullable=False)
    CategoryID = Column(UNIQUEIDENTIFIER, ForeignKey("Categories.CategoryID"), nullable=False)
    TransactionType = Column(String(20), nullable=False)  # 'income' or 'expense'
    Amount = Column(Numeric(15,2), nullable=False)
    Description = Column(String(500))
    TransactionDate = Column(Date, nullable=False)
    TransactionTime = Column(Time, default=lambda: datetime.utcnow().time())
    PaymentMethod = Column(String(50))
    Location = Column(String(255))
    Tags = Column(String)  # JSON string for multiple tags
    ReceiptURL = Column(String(500))
    Notes = Column(String)
    IsRecurring = Column(Boolean, default=False)
    RecurringPattern = Column(String)  # JSON string for recurring pattern
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    CreatedBy = Column(String(20), default="manual")
    
    # Relationships (optional)
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
