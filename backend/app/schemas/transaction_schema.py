# schemas/transaction_schema.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import date, time, datetime
from typing import Optional, List
from decimal import Decimal
import json

class TransactionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    category_id: UUID = Field(..., description="Category ID for the transaction")
    transaction_type: str = Field(..., description="Type of transaction: 'income' or 'expense'")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    transaction_date: date = Field(..., description="Date of the transaction")
    transaction_time: Optional[time] = Field(None, description="Time of the transaction")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method used")
    location: Optional[str] = Field(None, max_length=255, description="Transaction location")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    receipt_url: Optional[str] = Field(None, max_length=500, description="URL to receipt image/document")
    notes: Optional[str] = Field(None, description="Additional notes")
    is_recurring: bool = Field(False, description="Whether transaction is recurring")
    recurring_pattern: Optional[str] = Field(None, description="Recurring pattern (JSON)")
    created_by: str = Field("manual", max_length=20, description="How the transaction was created")

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        if v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    category_id: Optional[UUID] = None
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = Field(None, max_length=500)
    transaction_date: Optional[date] = None
    transaction_time: Optional[time] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    receipt_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_pattern: Optional[str] = None
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() not in ['income', 'expense']:
            raise ValueError('Transaction type must be either "income" or "expense"')
        return v.lower() if v else v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v

class TransactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: float,
            UUID: str
        }
    )
    
    transaction_id: UUID
    user_id: UUID
    category_id: UUID
    transaction_type: str
    amount: Decimal
    description: Optional[str]
    transaction_date: date
    transaction_time: Optional[time]
    payment_method: Optional[str]
    location: Optional[str]
    tags: Optional[List[str]]
    receipt_url: Optional[str]
    notes: Optional[str]
    is_recurring: bool
    recurring_pattern: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v) -> Optional[List[str]]:
        if isinstance(v, str) and v:
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]  # Single tag as string
        return v

class TransactionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total_income: Decimal
    total_expense: Decimal
    net_amount: Decimal
    transaction_count: int

class TransactionFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    category_id: Optional[UUID] = None
    transaction_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = None