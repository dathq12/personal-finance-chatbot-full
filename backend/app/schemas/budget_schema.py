from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class BudgetBase(BaseModel):
    user_id: UUID
    budget_name: str
    budget_type: str
    amount: float
    period_start: date
    period_end: date
    alert_threshold: float = 80.0

class BudgetCreate(BudgetBase):
    category_id: Optional[UUID] = None

class BudgetResponse(BudgetBase):
    budget_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BudgetAlertBase(BaseModel):
    budget_id: UUID
    user_id: UUID
    alert_type: str
    current_amount: float
    budget_amount: float
    percentage_used: float
    message: Optional[str] = None

class BudgetAlertCreate(BudgetAlertBase):
    pass

class BudgetAlertResponse(BudgetAlertBase):
    alert_id: UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True