# schemas/budget_schema.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

class BudgetTypeEnum(str, Enum):
    monthly = "monthly"
    weekly = "weekly"
    yearly = "yearly"

# ===== Budget =====
class BudgetBase(BaseModel):
    budget_name: str = Field(..., max_length=255, description="Budget name")
    budget_type: BudgetTypeEnum = Field(..., description="Budget type: monthly, weekly, yearly")
    amount: Decimal = Field(..., gt=0, description="Budget amount (must be positive)")
    period_start: date = Field(..., description="Budget period start date")
    period_end: date = Field(..., description="Budget period end date")
    auto_adjust: Optional[bool] = Field(False, description="Auto adjust budget")
    alert_threshold: Optional[Decimal] = Field(Decimal('80.0'), ge=0, le=100, description="Alert threshold percentage")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('period_end')
    @classmethod
    def validate_period_end(cls, v: date, info) -> date:
        if 'period_start' in info.data and v <= info.data['period_start']:
            raise ValueError('Period end must be after period start')
        return v

class BudgetCreate(BudgetBase):
    # category_display_name: str = Field(...,max_length=100, description= "Display name of category")
    pass

class BudgetUpdate(BaseModel):
    budget_name: Optional[str] = Field(None, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    auto_adjust: Optional[bool] = None
    alert_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v

class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    BudgetID: UUID = Field(..., description="Unique identifier for the budget")
    UserID: UUID
    budget_name: str
    budget_type: str
    amount: Decimal
    period_start: date
    period_end: date
    total_spent: Decimal
    auto_adjust: bool
    alert_threshold: Decimal
    is_active: bool
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

# ===== Budget Category =====
class BudgetCategoryBase(BaseModel):
    # user_category_id: UUID = Field(..., description="User category ID")
    allocated_amount: Decimal = Field(..., ge=0, description="Allocated amount for this category")

    @field_validator('allocated_amount')
    @classmethod
    def validate_allocated_amount(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError('Allocated amount must be non-negative')
        return v

class BudgetCategoryCreate(BudgetCategoryBase):
    category_display_name: str = Field(..., max_length=100, description="Display name of the category")
    pass

class BudgetCategoryUpdate(BaseModel):
    allocated_amount: Optional[Decimal] = Field(None, ge=0)

    @field_validator('allocated_amount')
    @classmethod
    def validate_allocated_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError('Allocated amount must be non-negative')
        return v

class BudgetCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    BudgetCategoryID: UUID
    BudgetID: UUID
    UserCategoryID: UUID
    category_display_name: str
    allocated_amount: Decimal
    spent_amount: Decimal
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

# ===== Budget Overview & Analysis =====
class BudgetCategoryOverview(BaseModel):
    """Budget category overview with actual spending"""
    user_category_id: UUID
    category_name: str
    allocated_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
    over_budget: bool
    variance: Decimal  # positive = under budget, negative = over budget
    variance_percentage: Decimal

class BudgetOverviewResponse(BaseModel):
    """Complete budget overview"""
    budget_id: UUID
    budget_name: str
    budget_type: str
    period_start: date
    period_end: date
    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    overall_percentage_used: Decimal
    categories: List[BudgetCategoryOverview]
    is_over_budget: bool
    days_remaining: int
    daily_average_spent: Decimal
    projected_total: Optional[Decimal] = None

class BudgetVsActualResponse(BaseModel):
    """Budget vs Actual comparison"""
    budget_id: UUID
    budget_name: str
    period_start: date
    period_end: date
    summary: Dict[str, Any] = Field(..., description="Overall summary statistics")
    categories: List[BudgetCategoryOverview]
    spending_trend: List[Dict[str, Any]] = Field(..., description="Daily/weekly spending trend")
    alerts: Optional[List[str]] = Field(..., description="Budget alerts and warnings")

class BudgetPerformanceMetrics(BaseModel):
    """Budget performance metrics"""
    budget_accuracy: Decimal = Field(..., description="How close actual spending is to budget")
    category_accuracy: Dict[str, Decimal] = Field(..., description="Accuracy per category")
    spending_consistency: Decimal = Field(..., description="Consistency of spending patterns")
    budget_utilization: Decimal = Field(..., description="Overall budget utilization percentage")
    over_budget_categories: int = Field(..., description="Number of categories over budget")
    under_budget_categories: int = Field(..., description="Number of categories under budget")

# ===== Budget Alert =====
class BudgetAlertBase(BaseModel):
    alert_type: str = Field(..., max_length=20, description="Type of alert")
    current_amount: Decimal = Field(..., ge=0, description="Current spent amount")
    percentage_used: Decimal = Field(..., ge=0, le=100, description="Percentage of budget used")
    message: Optional[str] = Field(None, description="Alert message")

class BudgetAlertCreate(BudgetAlertBase):
    budget_id: UUID
    budget_category_id: Optional[UUID] = None

class BudgetAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    AlertID: UUID
    BudgetID: UUID
    BudgetCategoryID: Optional[UUID] = None
    UserID: UUID
    alert_type: str
    current_amount: Decimal
    percentage_used: Decimal
    message: Optional[str] = None
    is_read: bool
    CreatedAt: datetime

# ===== Budget List Response =====
class BudgetListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    budgets: List[BudgetResponse] = Field(..., description="List of budgets")
    total_count: int = Field(..., description="Total number of budgets")

# ===== Budget Filter =====
class BudgetFilter(BaseModel):
    budget_type: Optional[str] = Field(None, description="Filter by budget type")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    date_from: Optional[date] = Field(None, description="Filter by period start date")
    date_to: Optional[date] = Field(None, description="Filter by period end date")
    
    # Pagination
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of records to return")

    # Sorting
    sort_by: Optional[str] = Field("CreatedAt", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort direction: 'asc' or 'desc'")

    @field_validator('budget_type')
    @classmethod
    def validate_budget_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['monthly', 'weekly', 'yearly']:
            raise ValueError('Budget type must be monthly, weekly, or yearly')
        return v

    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ['asc', 'desc']:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v

# ===== Analysis Request Models =====
class BudgetAnalysisRequest(BaseModel):
    budget_ids: Optional[List[UUID]] = Field(None, description="Specific budget IDs to analyze")
    include_categories: bool = Field(True, description="Include category breakdown")
    include_trends: bool = Field(True, description="Include spending trends")
    include_projections: bool = Field(True, description="Include budget projections")

class BudgetComparisonRequest(BaseModel):
    budget_ids: List[UUID] = Field(..., description="Budget IDs to compare", min_items=2, max_items=5)
    comparison_type: str = Field("performance", description="Type of comparison: performance, spending, categories")
    
    @field_validator('comparison_type')
    @classmethod
    def validate_comparison_type(cls, v: str) -> str:
        if v not in ['performance', 'spending', 'categories', 'trends']:
            raise ValueError('Comparison type must be performance, spending, categories, or trends')
        return v