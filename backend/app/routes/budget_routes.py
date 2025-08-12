# routers/budget.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta

from database import get_db
from schemas.budget_schema import (
    BudgetCreate, 
    BudgetUpdate, 
    BudgetResponse, 
    BudgetListResponse,
    BudgetFilter,
    BudgetCategoryCreate,
    BudgetCategoryUpdate,
    BudgetCategoryResponse,
    BudgetOverviewResponse,
    BudgetVsActualResponse,
    # BudgetPerformanceMetrics,
    BudgetAnalysisRequest,
    BudgetComparisonRequest
)
from crud import budget_crud
from auth.auth_dependency import get_current_user  

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
    dependencies=[Depends(HTTPBearer())]
)

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new budget"""
    created_budget = budget_crud.create_budget(
        db=db,
        user_id=current_user.UserID,
        budget_data=budget,
    )
    
    return created_budget

@router.get("/", response_model=BudgetListResponse)
def get_budgets(
    budget_type: Optional[str] = Query(None, description="Filter by budget type: 'monthly', 'weekly', 'yearly'"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    date_from: Optional[date] = Query(None, description="Filter by period start date YYYY-MM-DD"),
    date_to: Optional[date] = Query(None, description="Filter by period end date YYYY-MM-DD"),

    skip: int = Query(0, ge=0, description="Number of budgets to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of budgets to return per page"),

    sort_by: Optional[str] = Query("CreatedAt", description="Field to sort by 'BudgetName', 'Amount', 'CreatedAt',..."),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Sort order: 'asc' for ascending, 'desc' for descending"),

    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of budgets with optional filters, pagination, and sorting."""
    # Validate budget type
    if budget_type and budget_type not in ['monthly', 'weekly', 'yearly']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid budget type. Must be 'monthly', 'weekly', or 'yearly'."
        )

    # Get budgets with filters, pagination, and sorting
    filters = BudgetFilter(
        budget_type=budget_type,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return budget_crud.get_budgets(
        db=db,
        user_id=current_user.UserID,
        filters=filters
    )

@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a single budget by ID."""
    budget = budget_crud.get_budget_by_id(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy ngân sách."
        )
    
    return budget

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing budget."""
    # Check if budget exists
    existing_budget = budget_crud.get_budget_by_id(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    if not existing_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy ngân sách."
        )
    
    # Update budget
    updated_budget = budget_crud.update_budget(
        db=db,
        budget_id=budget_id,
        budget_data=budget_update,
        user_id=current_user.UserID
    )
    
    if not updated_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không thể cập nhật ngân sách."
        )
    
    return updated_budget

@router.delete("/{budget_id}", status_code=status.HTTP_200_OK)
def delete_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a budget"""
    existing_budget = budget_crud.get_budget_by_id(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    if not existing_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy ngân sách."
        )
    
    success = budget_crud.delete_budget(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa ngân sách."
        )
    
    return {"detail": "Ngân sách đã được xóa thành công."}

# Budget Category endpoints
@router.post("/{budget_id}/categories", response_model=BudgetCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_budget_category(
    budget_id: UUID,
    category: BudgetCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a budget category"""
    created_category = budget_crud.create_budget_category(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID,
        category_data=category
    )
    
    if not created_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngân sách."
        )
    
    return created_category

@router.get("/{budget_id}/categories", response_model=List[BudgetCategoryResponse])
def get_budget_categories(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all categories for a budget"""
    categories = budget_crud.get_budget_categories(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    return categories

# NEW: Budget Overview and Analysis Endpoints

@router.get("/{budget_id}/overview", response_model=BudgetOverviewResponse)
def get_budget_overview(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive budget overview with actual spending comparison"""
    overview = budget_crud.get_budget_overview(
        db=db,
        user_id=current_user.UserID,
        budget_id=budget_id
    )
    
    if not overview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngân sách."
        )
    
    # Update spent amounts in real-time
    budget_crud.update_budget_spent_amounts(db, current_user.UserID, budget_id)
    
    return overview

@router.get("/{budget_id}/vs-actual", response_model=BudgetVsActualResponse)
def get_budget_vs_actual(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare budgeted amounts with actual spending"""
    comparison = budget_crud.get_budget_vs_actual(
        db=db,
        user_id=current_user.UserID,
        budget_id=budget_id
    )
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngân sách."
        )
    
    return comparison

# @router.get("/{budget_id}/performance", response_model=BudgetPerformanceMetrics)
# def get_budget_performance(
#     budget_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get budget performance metrics and analysis"""
#     metrics = budget_crud.get_budget_performance_metrics(
#         db=db,
#         user_id=current_user.UserID,
#         budget_id=budget_id
#     )
    
#     if not metrics:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Không tìm thấy ngân sách."
#         )
    
#     return metrics

@router.post("/{budget_id}/sync")
def sync_budget_spending(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Manually sync budget with actual spending data"""
    # Verify budget exists
    budget = budget_crud.get_budget_by_id(
        db=db,
        budget_id=budget_id,
        user_id=current_user.UserID
    )
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngân sách."
        )
    
    # Update spent amounts
    budget_crud.update_budget_spent_amounts(db, current_user.UserID, budget_id)
    
    return {"detail": "Đã đồng bộ dữ liệu chi tiêu thực tế."}

# Additional useful endpoints
@router.get("/by-type/{budget_type}", response_model=BudgetListResponse)
def get_budgets_by_type(
    budget_type: str,
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of budgets to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of budgets to return per page"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get budgets filtered by budget type."""
    # Validate budget type
    if budget_type not in ['monthly', 'weekly', 'yearly']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid budget type. Must be 'monthly', 'weekly', or 'yearly'."
        )
    
    filters = BudgetFilter(
        budget_type=budget_type,
        is_active=is_active,
        skip=skip,
        limit=limit,
        sort_by="CreatedAt",
        sort_order="desc"
    )
    
    return budget_crud.get_budgets(
        db=db,
        user_id=current_user.UserID,
        filters=filters
    )

@router.get("/active/summary")
def get_active_budgets_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get summary of active budgets with overview data."""
    overviews = budget_crud.get_active_budgets_with_overview(
        db=db,
        user_id=current_user.UserID
    )
    
    if not overviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy ngân sách đang hoạt động."
        )
    
    # Calculate overall statistics
    total_budget = sum(overview.total_budget for overview in overviews)
    total_spent = sum(overview.total_spent for overview in overviews)
    total_remaining = sum(overview.total_remaining for overview in overviews)
    
    # Count statistics
    over_budget_count = sum(1 for overview in overviews if overview.is_over_budget)
    categories_over_budget = sum(
        sum(1 for cat in overview.categories if cat.over_budget) 
        for overview in overviews
    )
    
    return {
        "total_active_budgets": len(overviews),
        "total_budget_amount": float(total_budget),
        "total_spent": float(total_spent),
        "total_remaining": float(total_remaining),
        "overall_percentage_used": float((total_spent / total_budget * 100) if total_budget > 0 else 0),
        "budgets_over_budget": over_budget_count,
        "categories_over_budget": categories_over_budget,
        "budgets": [
            {
                "budget_id": str(overview.budget_id),
                "budget_name": overview.budget_name,
                "budget_type": overview.budget_type,
                "percentage_used": float(overview.overall_percentage_used),
                "is_over_budget": overview.is_over_budget,
                "days_remaining": overview.days_remaining,
                "total_budget": float(overview.total_budget),
                "total_spent": float(overview.total_spent)
            }
            for overview in overviews
        ]
    }

@router.get("/categories/spending-comparison")
def get_category_spending_comparison(
    category_ids: str = Query(..., description="Comma-separated list of category IDs"),
    date_from: Optional[date] = Query(None, description="Start date for comparison"),
    date_to: Optional[date] = Query(None, description="End date for comparison"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Compare spending across multiple categories"""
    try:
        # Parse category IDs
        parsed_category_ids = [id.strip() for id in category_ids.split(',')]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category ID format"
        )
    
    # Set default date range if not provided
    if not date_from:
        date_from = date.today().replace(day=1)  # First day of current month
    if not date_to:
        date_to = date.today()
    
    comparison = budget_crud.get_category_spending_comparison(
        db=db,
        user_id=current_user.UserID,
        category_ids=parsed_category_ids,
        date_from=date_from,
        date_to=date_to
    )
    
    return comparison

@router.get("/analysis/dashboard")
def get_budget_dashboard(
    period_type: str = Query("monthly", description="Analysis period: daily, weekly, monthly"),
    include_projections: bool = Query(True, description="Include spending projections"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive budget dashboard data"""
    # Get active budgets with overview
    overviews = budget_crud.get_active_budgets_with_overview(
        db=db,
        user_id=current_user.UserID
    )
    
    if not overviews:
        return {
            "message": "No active budgets found",
            "budgets": [],
            "summary": {},
            "trends": [],
            "alerts": []
        }
    
    # Calculate dashboard metrics
    total_budget = sum(overview.total_budget for overview in overviews)
    total_spent = sum(overview.total_spent for overview in overviews)
    
    # Collect all alerts
    all_alerts = []
    for overview in overviews:
        vs_actual = budget_crud.get_budget_vs_actual(db, current_user.UserID, overview.budget_id)
        if vs_actual:
            all_alerts.extend(vs_actual.alerts)
    
    # Get spending trends for all budgets
    trends_data = []
    for overview in overviews:
        vs_actual = budget_crud.get_budget_vs_actual(db, current_user.UserID, overview.budget_id)
        if vs_actual:
            trends_data.append({
                "budget_name": overview.budget_name,
                "trend": vs_actual.spending_trend
            })
    
    return {
        "summary": {
            "total_budgets": len(overviews),
            "total_budget_amount": float(total_budget),
            "total_spent": float(total_spent),
            "total_remaining": float(total_budget - total_spent),
            "overall_percentage": float((total_spent / total_budget * 100) if total_budget > 0 else 0),
            "budgets_over_budget": sum(1 for overview in overviews if overview.is_over_budget),
            "categories_over_budget": sum(
                sum(1 for cat in overview.categories if cat.over_budget) 
                for overview in overviews
            )
        },
        "budgets": [
            {
                "budget_id": str(overview.budget_id),
                "budget_name": overview.budget_name,
                "budget_type": overview.budget_type,
                "percentage_used": float(overview.overall_percentage_used),
                "is_over_budget": overview.is_over_budget,
                "days_remaining": overview.days_remaining,
                "top_categories": [
                    {
                        "name": cat.category_name,
                        "percentage": float(cat.percentage_used),
                        "over_budget": cat.over_budget
                    }
                    for cat in sorted(overview.categories, key=lambda x: x.percentage_used, reverse=True)[:3]
                ]
            }
            for overview in overviews
        ],
        "trends": trends_data,
        "alerts": all_alerts[:10],  # Limit to top 10 alerts
        "generated_at": datetime.now().isoformat()
    }