# schemas/budget_schema.py
from pydantic import BaseModel, ConfigDict, Field, field_validator , ValidationInfo
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID
from enum import Enum

class BudgetType(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly" 
    YEARLY = "yearly"

class AlertType(str, Enum):
    WARNING = "warning"
    EXCEEDED = "exceeded"
    NEAR_LIMIT = "near_limit"

# ==================== BUDGET SCHEMAS ====================


class BudgetBase(BaseModel):
    budget_name: str = Field(..., min_length=1, max_length=255, alias='BudgetName')
    budget_type: BudgetType = Field(..., alias='BudgetType')
    amount: Decimal = Field(..., gt=0, decimal_places=2, alias='Amount')
    period_start: date = Field(..., alias='PeriodStart')
    period_end: date = Field(..., alias='PeriodEnd')
    auto_adjust: bool = Field(False, alias='AutoAdjust')
    include_income: bool = Field(False, alias='IncludeIncome')
    alert_threshold: Decimal = Field(default=Decimal("80.00"), ge=0, le=100, decimal_places=2, alias='AlertThreshold')

    model_config = ConfigDict(from_attributes=True)


    @field_validator('period_end')
    @classmethod
    def period_end_must_be_after_start(cls, v, info: ValidationInfo):
        period_start = info.data.get('period_start')
        if period_start and v <= period_start:
            raise ValueError('Period end must be after period start')
        return v

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    budget_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    auto_adjust: Optional[bool] = None
    include_income: Optional[bool] = None
    alert_threshold: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    is_active: Optional[bool] = None

    @field_validator('period_end')
    @classmethod
    def period_end_must_be_after_start(cls, v, info: ValidationInfo):
        period_start = info.data.get('period_start')
        if v and period_start and v <= period_start:
            raise ValueError('Period end must be after period start')
        return v

class BudgetResponse(BudgetBase):
    budget_id: UUID = Field(alias='BudgetID')
    user_id: UUID = Field(alias='UserID')
    is_active: bool = Field(alias='IsActive')
    created_at: datetime = Field(alias='CreatedAt')
    updated_at: datetime = Field(alias='UpdatedAt')

    model_config = ConfigDict(from_attributes=True)
class BudgetSummary(BaseModel):
    budget_id: UUID
    budget_name: str
    amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
    budget_type: BudgetType
    period_start: date
    period_end: date
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
 

# ==================== BUDGET CATEGORY SCHEMAS ====================

class BudgetCategoryBase(BaseModel):
    budget_id: UUID
    user_category_id: UUID
    allocated_amount: Decimal = Field(..., ge=0, decimal_places=2)

class BudgetCategoryCreate(BudgetCategoryBase):
    pass

class BudgetCategoryUpdate(BaseModel):
    allocated_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

class BudgetCategoryResponse(BudgetCategoryBase):
    budget_category_id: UUID
    spent_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BudgetCategoryDetail(BudgetCategoryResponse):
    category_display_name: str
    remaining_amount: Decimal
    percentage_used: Decimal

# ==================== BUDGET ALERT SCHEMAS ====================

class BudgetAlertBase(BaseModel):
    alert_type: AlertType
    current_amount: Decimal = Field(..., decimal_places=2)
    budget_amount: Decimal = Field(..., decimal_places=2)
    percentage_used: Decimal = Field(..., decimal_places=2)
    message: Optional[str] = None

class BudgetAlertCreate(BudgetAlertBase):
    budget_id: UUID
    user_id: UUID

class BudgetAlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    message: Optional[str] = None

class BudgetAlertResponse(BudgetAlertBase):
    alert_id: UUID
    budget_id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ==================== COMPOSITE SCHEMAS ====================

class BudgetWithCategories(BudgetResponse):
    budget_categories: List[BudgetCategoryDetail] = []
    total_allocated: Decimal
    total_spent: Decimal

class BudgetCreateWithCategories(BaseModel):
    budget: BudgetCreate
    categories: List[BudgetCategoryCreate] = []