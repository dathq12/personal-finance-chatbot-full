# schemas/transaction_schema.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import date, time, datetime
from typing import Optional, List, Union
from decimal import Decimal
import json

class TransactionBase(BaseModel):
    transaction_type: str = Field(..., description="Type of transaction: 'income' or 'expense'")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    transaction_date: date = Field(..., description="Date of the transaction")
    transaction_time: Optional[time] = Field(None, description="Time of the transaction")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method used")
    location: Optional[str] = Field(None, max_length=255, description="Location of the transaction")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes for the transaction")
    created_by: str = Field("manual", max_length=20, description="How the transaction was created")

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        if v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower()
        
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransactionCreate(TransactionBase):
    category_display_name: str = Field(..., max_length = 100, description = "Display name of the category")

class TransactionUpdate(BaseModel):
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: Optional[date] = None
    transaction_time: Optional[time] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    category_display_name: Optional[str] = Field(None, max_length=100, description="Display name of the category")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower() if v else v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v

    
class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    TransactionID: UUID = Field(..., description="Unique identifier for the transaction")
    UserID: UUID
    UserCategoryID: UUID
    transaction_type: str = Field(..., description="Type of transaction: 'income' or 'expense'")
    amount: Decimal = Field(..., description="Transaction amount")
    description: Optional[str] = Field(None, description="Transaction description")
    transaction_date: date = Field(..., description="Date of the transaction")
    transaction_time: Optional[time] = Field(None, description="Time of the transaction")
    payment_method: Optional[str] = Field(None, description="Payment method used")
    location: Optional[str] = Field(None, description="Location of the transaction")
    notes: Optional[str] = Field(None, description="Additional notes for the transaction")
    created_by: str = Field(..., description="How the transaction was created")
    category_display_name: str = Field(..., description="Display name of the category")
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

class TransactionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction: List[TransactionResponse] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    total_income: Decimal = Field(..., description="Total income from transactions")
    total_expense: Decimal = Field(..., description="Total expense from transactions")
    net_amount: Decimal = Field(..., description="Net amount (income - expense)")

class TransactionFilter(BaseModel):
    transaction_type: Optional[str] = Field(
        None, description="Filter by transaction type: 'income' or 'expense'"
    )
    category_display_name: Optional[str] = Field(
        None, description="Filter by category display name"
    )
    payment_method: Optional[str] = Field(
        None, description="Filter by payment method"
    )
    location: Optional[str] = Field(
        None, description="Filter by location"
    )
    date_from: Optional[Union[str, date]] = Field(
        None, description="Filter by start date (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)"
    )
    date_to: Optional[Union[str, date]] = Field(
        None, description="Filter by end date (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)"
    )
    amount_min: Optional[Decimal] = Field(
        None, description="Minimum transaction amount"
    )
    amount_max: Optional[Decimal] = Field(
        None, description="Maximum transaction amount"
    )
    search: Optional[str] = Field(
        None, description="Search text in transaction details"
    )
    created_by: Optional[str] = Field(
        None, description="Transaction source: 'manual' or 'imported'"
    )

    # Pagination
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of records to return")

    # Sorting
    sort_by: Optional[str] = Field("transaction_date", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort direction: 'asc' or 'desc'")

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower() if v else v
    
    @field_validator('created_by')
    @classmethod
    def validate_created_by(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['manual', 'imported']:
            raise ValueError('Created by must be either "manual" or "imported"')
        return v.lower() if v else v
    
    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v
    
    @field_validator('date_from', 'date_to')
    @classmethod
    def parse_custom_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Try different date formats
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            raise ValueError("Invalid date format. Supported formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY")
        return v
