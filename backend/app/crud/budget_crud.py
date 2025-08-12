# crud/budget_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from fastapi import HTTPException, status

from models.transaction import Transaction
from models.budget import Budget, BudgetCategory, BudgetAlert
from schemas.budget_schema import (
    BudgetCreate, 
    BudgetUpdate, 
    BudgetResponse,
    BudgetFilter,
    BudgetListResponse,
    BudgetCategoryCreate,
    BudgetCategoryUpdate,
    BudgetCategoryResponse,
    BudgetOverviewResponse,
    BudgetCategoryOverview,
    BudgetVsActualResponse,
    BudgetPerformanceMetrics
)
from crud.category_crud import get_category_display_name, get_user_category_id_by_display_name

def create_budget(
    db: Session, 
    user_id: UUID, 
    budget_data: BudgetCreate
) -> BudgetResponse:
    """Create a new budget"""
    db_budget = Budget(
        UserID=user_id,
        BudgetName=budget_data.budget_name,
        BudgetType=budget_data.budget_type.value,
        Amount=budget_data.amount,
        PeriodStart=budget_data.period_start,
        PeriodEnd=budget_data.period_end,
        AutoAdjust=budget_data.auto_adjust,
        AlertThreshold=budget_data.alert_threshold
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)

    # Convert budget object to dict for response
    budget_dict = {
        'BudgetID': db_budget.BudgetID,
        'UserID': db_budget.UserID,
        'budget_name': db_budget.BudgetName,
        'budget_type': db_budget.BudgetType,
        'amount': db_budget.Amount,
        'period_start': db_budget.PeriodStart,
        'period_end': db_budget.PeriodEnd,
        'total_spent': db_budget.TotalSpent,
        'auto_adjust': db_budget.AutoAdjust,
        'alert_threshold': db_budget.AlertThreshold,
        'is_active': db_budget.IsActive,
        'CreatedAt': db_budget.CreatedAt,
        'UpdatedAt': db_budget.UpdatedAt
    }
    
    return BudgetResponse(**budget_dict)

def get_budget_by_id(
    db: Session, 
    user_id: UUID, 
    budget_id: UUID
) -> Optional[BudgetResponse]:
    """Get a budget by ID"""
    budget = (
        db.query(Budget)
        .filter(
            Budget.BudgetID == budget_id,
            Budget.UserID == user_id
        )
        .first()
    )
    if not budget:
        return None

    budget_dict = {
        'BudgetID': budget.BudgetID,
        'UserID': budget.UserID,
        'budget_name': budget.BudgetName,
        'budget_type': budget.BudgetType,
        'amount': budget.Amount,
        'period_start': budget.PeriodStart,
        'period_end': budget.PeriodEnd,
        'total_spent': budget.TotalSpent,
        'auto_adjust': budget.AutoAdjust,
        'alert_threshold': budget.AlertThreshold,
        'is_active': budget.IsActive,
        'CreatedAt': budget.CreatedAt,
        'UpdatedAt': budget.UpdatedAt
    }
    
    return BudgetResponse(**budget_dict)

def get_budgets(
    db: Session, 
    user_id: UUID, 
    filters: BudgetFilter
) -> BudgetListResponse:
    """Get budgets with optional filters"""
    # Build base query
    query = db.query(Budget).filter(Budget.UserID == user_id)
    
    # Apply filters
    if filters.budget_type:
        query = query.filter(Budget.BudgetType == filters.budget_type)
    
    if filters.is_active is not None:
        query = query.filter(Budget.IsActive == filters.is_active)
    
    if filters.date_from:
        query = query.filter(Budget.PeriodStart >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(Budget.PeriodEnd <= filters.date_to)

    # Count total budgets
    total_count = query.count()

    # Apply sorting
    sort_field = getattr(Budget, filters.sort_by, Budget.CreatedAt)
    if filters.sort_order == 'desc':
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))

    # Apply pagination
    query = query.offset(filters.skip).limit(filters.limit)

    # Execute query and get results
    results = query.all()

    budgets = []
    for budget in results:
        budget_dict = {
            'BudgetID': budget.BudgetID,
            'UserID': budget.UserID,
            'budget_name': budget.BudgetName,
            'budget_type': budget.BudgetType,
            'amount': budget.Amount,
            'period_start': budget.PeriodStart,
            'period_end': budget.PeriodEnd,
            'total_spent': budget.TotalSpent,
            'auto_adjust': budget.AutoAdjust,
            'alert_threshold': budget.AlertThreshold,
            'is_active': budget.IsActive,
            'CreatedAt': budget.CreatedAt,
            'UpdatedAt': budget.UpdatedAt
        }
        budgets.append(BudgetResponse(**budget_dict))

    return BudgetListResponse(
        budgets=budgets,
        total_count=total_count
    )

def update_budget(
    db: Session, 
    user_id: UUID, 
    budget_id: UUID, 
    budget_data: BudgetUpdate
) -> Optional[BudgetResponse]:
    """Update an existing budget"""
    budget = (
        db.query(Budget)
        .filter(
            Budget.BudgetID == budget_id,
            Budget.UserID == user_id
        )
        .first()
    )
    if not budget:
        return None

    # Update budget fields
    update_data = budget_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'budget_name':
            setattr(budget, 'BudgetName', value)
        elif key == 'is_active':
            setattr(budget, 'IsActive', value)
        elif key == 'auto_adjust':
            setattr(budget, 'AutoAdjust', value)
        elif key == 'alert_threshold':
            setattr(budget, 'AlertThreshold', value)
        elif key == 'period_start':
            setattr(budget, 'PeriodStart', value)
        elif key == 'period_end':
            setattr(budget, 'PeriodEnd', value)
        else:
            # Capitalize first letter for other fields
            field_name = key.capitalize()
            setattr(budget, field_name, value)

    db.commit()
    db.refresh(budget)

    budget_dict = {
        'BudgetID': budget.BudgetID,
        'UserID': budget.UserID,
        'budget_name': budget.BudgetName,
        'budget_type': budget.BudgetType,
        'amount': budget.Amount,
        'period_start': budget.PeriodStart,
        'period_end': budget.PeriodEnd,
        'total_spent': budget.TotalSpent,
        'auto_adjust': budget.AutoAdjust,
        'alert_threshold': budget.AlertThreshold,
        'is_active': budget.IsActive,
        'CreatedAt': budget.CreatedAt,
        'UpdatedAt': budget.UpdatedAt
    }
    
    return BudgetResponse(**budget_dict)

def delete_budget(db: Session, budget_id: UUID, user_id: UUID) -> bool:
    """Delete a budget"""
    budget = (
        db.query(Budget)
        .filter(
            Budget.BudgetID == budget_id,
            Budget.UserID == user_id
        )
        .first()
    )
    
    if not budget:
        return False
    
    db.delete(budget)
    db.commit()
    return True

# Budget Category CRUD functions
def create_budget_category(
    db: Session,
    budget_id: UUID,
    user_id: UUID,
    category_data: BudgetCategoryCreate
) -> Optional[BudgetCategoryResponse]:
    """Create a budget category"""
    # Verify budget belongs to user
    budget = db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id
    ).first()
    
    if not budget:
        return None

    user_category_id = get_user_category_id_by_display_name(
        db=db,
        user_id=user_id,
        display_name=category_data.category_display_name,
        transaction_type= "expense"  # Assuming expense category for budget
    )
    if not user_category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy danh mục '{category_data.category_display_name}'"
        )

    db_category = BudgetCategory(
        BudgetID=budget_id,
        UserCategoryID= user_category_id,
        AllocatedAmount=category_data.allocated_amount
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    category_dict = {
        'BudgetCategoryID': db_category.BudgetCategoryID,
        'BudgetID': db_category.BudgetID,
        'UserCategoryID': db_category.UserCategoryID,
        'category_display_name': category_data.category_display_name,
        'allocated_amount': db_category.AllocatedAmount,
        'spent_amount': db_category.SpentAmount,
        'CreatedAt': db_category.CreatedAt,
        'UpdatedAt': db_category.UpdatedAt
    }
    
    return BudgetCategoryResponse(**category_dict)

def get_budget_categories(
    db: Session,
    budget_id: UUID,
    user_id: UUID
) -> List[BudgetCategoryResponse]:
    """Get all categories for a budget"""
    # Verify budget belongs to user
    budget = db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id
    ).first()
    
    if not budget:
        return []


    categories = db.query(BudgetCategory).filter(
        BudgetCategory.BudgetID == budget_id
    ).all()

    result = []
    for category in categories:
        category_dict = {
            'BudgetCategoryID': category.BudgetCategoryID,
            'BudgetID': category.BudgetID,
            'UserCategoryID': category.UserCategoryID,
            'category_display_name': get_category_display_name(
                db=db,
                user_category_id=category.UserCategoryID),
            'allocated_amount': category.AllocatedAmount,
            'spent_amount': category.SpentAmount,
            'CreatedAt': category.CreatedAt,
            'UpdatedAt': category.UpdatedAt
        }
        result.append(BudgetCategoryResponse(**category_dict))
    
    return result

# NEW: Budget Overview and Analysis Functions

def get_actual_spending_by_category(
    db: Session,
    user_id: UUID,
    date_from: date,
    date_to: date
) -> Dict[UUID, Decimal]:
    """Get actual spending by user category within date range"""
    # This assumes you have Transaction, UserCategory, Category tables
    # Adjust table names according to your actual schema
    query = text("""
        SELECT 
            uc.UserCategoryID,
            COALESCE(SUM(t.Amount), 0) as total_spent
        FROM UserCategories uc
        LEFT JOIN Transactions t ON uc.UserCategoryID = t.UserCategoryID 
            AND t.UserID = :user_id 
            AND t.TransactionType = 'expense'
            AND t.TransactionDate >= :date_from 
            AND t.TransactionDate <= :date_to
        WHERE uc.UserID = :user_id
        GROUP BY uc.UserCategoryID
    """)
    
    results = db.execute(query, {
        'user_id': user_id,
        'date_from': date_from,
        'date_to': date_to
    }).fetchall()
    
    return {UUID(row.UserCategoryID): Decimal(row.total_spent or 0) for row in results}

def update_budget_spent_amounts(
    db: Session,
    user_id: UUID,
    budget_id: UUID
) -> None:
    """
    Update SpentAmount for all categories in a budget
    """
    # Lấy toàn bộ budget categories thuộc budget của user
    categories = db.query(BudgetCategory).filter(
        BudgetCategory.BudgetID == budget_id
    ).all()

    for category in categories:
        spent_total = (
            db.query(func.coalesce(func.sum(Transaction.Amount), 0))
            .filter(
                Transaction.UserID == user_id,
                Transaction.UserCategoryID == category.UserCategoryID,
                Transaction.TransactionType == 'expense'
            )
            .scalar()
        )
        category.SpentAmount = spent_total

    db.commit()

def get_budget_overview(
    db: Session,
    user_id: UUID,
    budget_id: UUID
) -> Optional[BudgetOverviewResponse]:
    """Get comprehensive budget overview with actual spending"""
    # Get budget details
    budget = get_budget_by_id(db, user_id, budget_id)
    if not budget:
        return None
    
    # Get budget categories
    budget_categories = get_budget_categories(db, budget_id, user_id)
    
    # Get actual spending by category
    actual_spending = get_actual_spending_by_category(
        db, user_id, budget.period_start, budget.period_end
    )
    
    # Get category display names
    category_names = get_category_display_names(db, user_id)
    
    # Build category overviews
    category_overviews = []
    total_allocated = Decimal('0')
    total_spent = Decimal('0')
    
    for bc in budget_categories:
        spent = actual_spending.get(bc.UserCategoryID, Decimal('0'))
        remaining = bc.allocated_amount - spent
        percentage_used = (spent / bc.allocated_amount * 100) if bc.allocated_amount > 0 else Decimal('0')
        variance = bc.allocated_amount - spent
        variance_percentage = (variance / bc.allocated_amount * 100) if bc.allocated_amount > 0 else Decimal('0')
        
        category_overview = BudgetCategoryOverview(
            user_category_id=bc.UserCategoryID,
            category_name=category_names.get(bc.UserCategoryID, "Unknown Category"),
            allocated_amount=bc.allocated_amount,
            spent_amount=spent,
            remaining_amount=remaining,
            percentage_used=percentage_used,
            over_budget=spent > bc.allocated_amount,
            variance=variance,
            variance_percentage=variance_percentage
        )
        category_overviews.append(category_overview)
        
        total_allocated += bc.allocated_amount
        total_spent += spent
    
    # Calculate overall metrics
    total_remaining = total_allocated - total_spent
    overall_percentage = (total_spent / total_allocated * 100) if total_allocated > 0 else Decimal('0')
    is_over_budget = total_spent > total_allocated
    
    # Calculate days and projections
    today = date.today()
    if today <= budget.period_end:
        days_remaining = (budget.period_end - today).days
    else:
        days_remaining = 0
    
    period_days = (budget.period_end - budget.period_start).days
    days_elapsed = (min(today, budget.period_end) - budget.period_start).days + 1
    
    daily_average = total_spent / days_elapsed if days_elapsed > 0 else Decimal('0')
    projected_total = daily_average * period_days if period_days > 0 else None
    
    return BudgetOverviewResponse(
        budget_id=budget.BudgetID,
        budget_name=budget.budget_name,
        budget_type=budget.budget_type,
        period_start=budget.period_start,
        period_end=budget.period_end,
        total_budget=total_allocated,
        total_spent=total_spent,
        total_remaining=total_remaining,
        overall_percentage_used=overall_percentage,
        categories=category_overviews,
        is_over_budget=is_over_budget,
        days_remaining=days_remaining,
        daily_average_spent=daily_average,
        projected_total=projected_total
    )

def get_budget_vs_actual(
    db: Session,
    user_id: UUID,
    budget_id: UUID
) -> Optional[BudgetVsActualResponse]:
    """Get budget vs actual comparison with trends and alerts"""
    overview = get_budget_overview(db, user_id, budget_id)
    if not overview:
        return None
    
    # Get spending trends (daily aggregation)
    spending_trend = get_spending_trend(db, user_id, overview.period_start, overview.period_end)
    
    # Generate alerts
    alerts = generate_budget_alerts(overview)
    
    # Summary statistics
    summary = {
        "total_budget": float(overview.total_budget),
        "total_spent": float(overview.total_spent),
        "total_remaining": float(overview.total_remaining),
        "percentage_used": float(overview.overall_percentage_used),
        "days_remaining": overview.days_remaining,
        "daily_average": float(overview.daily_average_spent),
        "projected_total": float(overview.projected_total) if overview.projected_total else None,
        "is_over_budget": overview.is_over_budget,
        "categories_over_budget": sum(1 for cat in overview.categories if cat.over_budget),
        "categories_under_budget": sum(1 for cat in overview.categories if not cat.over_budget),
        "best_performing_category": min(overview.categories, key=lambda x: x.percentage_used).category_name if overview.categories else None,
        "worst_performing_category": max(overview.categories, key=lambda x: x.percentage_used).category_name if overview.categories else None
    }
    
    return BudgetVsActualResponse(
        budget_id=overview.budget_id,
        budget_name=overview.budget_name,
        period_start=overview.period_start,
        period_end=overview.period_end,
        summary=summary,
        categories=overview.categories,
        spending_trend=spending_trend,
        alerts=alerts
    )

def get_category_display_names(db: Session, user_id: UUID) -> Dict[UUID, str]:
    """Get category display names using coalesce logic"""
    query = text("""
        SELECT 
            uc.UserCategoryID,
            COALESCE(uc.CustomName, c.CategoryName) as category_display_name
        FROM UserCategories uc
        LEFT JOIN Categories c ON uc.CategoryID = c.CategoryID
        WHERE uc.UserID = :user_id
    """)
    
    results = db.execute(query, {'user_id': user_id}).fetchall()
    return {UUID(row.UserCategoryID): row.category_display_name for row in results}

def get_spending_trend(
    db: Session,
    user_id: UUID,
    date_from: date,
    date_to: date
) -> List[Dict[str, Any]]:
    """Get daily spending trend"""
    query = text("""
        SELECT 
            t.TransactionDate as date,
            SUM(t.Amount) as daily_spending
        FROM Transactions t
        WHERE t.UserID = :user_id 
            AND t.TransactionType = 'expense'
            AND t.TransactionDate >= :date_from 
            AND t.TransactionDate <= :date_to
        GROUP BY t.TransactionDate
        ORDER BY t.TransactionDate
    """)
    
    results = db.execute(query, {
        'user_id': user_id,
        'date_from': date_from,
        'date_to': date_to
    }).fetchall()
    
    return [
        {
            "date": row.date.isoformat(),
            "amount": float(row.daily_spending)
        }
        for row in results
    ]

def generate_budget_alerts(overview: BudgetOverviewResponse) -> List[str]:
    """Generate budget alerts based on overview data"""
    alerts = []
    
    # Overall budget alerts
    if overview.overall_percentage_used >= 90:
        alerts.append(f"Critical: You've used {overview.overall_percentage_used:.1f}% of your total budget!")
    elif overview.overall_percentage_used >= 75:
        alerts.append(f"Warning: You've used {overview.overall_percentage_used:.1f}% of your total budget.")
    
    # Category alerts
    for category in overview.categories:
        if category.percentage_used >= 100:
            alerts.append(f"Over budget: {category.category_name} is {category.percentage_used:.1f}% over budget!")
        elif category.percentage_used >= 90:
            alerts.append(f"Critical: {category.category_name} is at {category.percentage_used:.1f}% of budget.")
    