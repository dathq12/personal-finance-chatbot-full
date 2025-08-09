# routers/budget_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from fastapi.security import HTTPBearer

from app.database import get_db
from crud import budget_crud
from schemas.budget_schema import (
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummary, BudgetWithCategories,
    BudgetCategoryCreate, BudgetCategoryUpdate, BudgetCategoryResponse, BudgetCategoryDetail,
    BudgetAlertCreate, BudgetAlertResponse, BudgetCreateWithCategories
)
from auth.auth_dependency import get_current_user  # Giả định bạn có auth dependency

router = APIRouter(prefix="/budgets", tags=["budgets"], dependencies=[Depends(HTTPBearer())])

# ==================== BUDGET ENDPOINTS ====================

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tạo budget mới"""
    try:
        return budget_crud.create_budget(db, current_user.UserID, budget)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[BudgetResponse])
def get_user_budgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    budget_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách budgets của user"""
    return budget_crud.get_budgets_by_user(
        db, 
        current_user.UserID, 
        skip, 
        limit, 
        is_active, 
        budget_type
    )

@router.get("/count")
def get_budgets_count(
    is_active: Optional[bool] = Query(None),
    budget_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Đếm số lượng budgets của user"""
    count = budget_crud.get_budgets_count(
        db, 
        current_user.UserID, 
        is_active, 
        budget_type
    )
    return {"count": count}

@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy budget theo ID"""
    budget = budget_crud.get_budget(db, budget_id, current_user.UserID)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.get("/{budget_id}/summary", response_model=BudgetSummary)
def get_budget_summary(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy tóm tắt budget với thông tin chi tiêu"""
    summary = budget_crud.get_budget_summary(db, budget_id, current_user.UserID)
    if not summary:
        raise HTTPException(status_code=404, detail="Budget not found")
    return summary

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật budget"""
    updated_budget = budget_crud.update_budget(
        db, 
        budget_id, 
        current_user.UserID, 
        budget_update
    )
    if not updated_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return updated_budget

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: UUID,
    hard_delete: bool = Query(False, description="True for hard delete, False for soft delete"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Xóa budget (soft delete mặc định, hard delete nếu có tham số)"""
    if hard_delete:
        success = budget_crud.hard_delete_budget(db, budget_id, current_user.UserID)
    else:
        success = budget_crud.delete_budget(db, budget_id, current_user.UserID)
    
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return None

# ==================== BUDGET CATEGORY ENDPOINTS ====================

@router.post("/{budget_id}/categories", response_model=BudgetCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_budget_category(
    budget_id: UUID,
    budget_category: BudgetCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tạo budget category"""
    # Đảm bảo budget_id trong request body khớp với URL
    if budget_category.budget_id != budget_id:
        raise HTTPException(status_code=400, detail="Budget ID in URL and request body must match")
    
    try:
        return budget_crud.create_budget_category(db, current_user.UserID, budget_category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{budget_id}/categories", response_model=List[BudgetCategoryDetail])
def get_budget_categories(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách budget categories theo budget ID"""
    return budget_crud.get_budget_categories_by_budget(db, budget_id, current_user.UserID)

@router.get("/{budget_id}/categories/{budget_category_id}", response_model=BudgetCategoryResponse)
def get_budget_category(
    budget_id: UUID,
    budget_category_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy budget category theo ID"""
    budget_category = budget_crud.get_budget_category(db, budget_category_id, current_user.UserID)
    if not budget_category:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    # Kiểm tra budget_id có khớp không
    if budget_category.BudgetID != str(budget_id):
        raise HTTPException(status_code=400, detail="Budget category does not belong to this budget")
    
    return budget_category

@router.put("/{budget_id}/categories/{budget_category_id}", response_model=BudgetCategoryResponse)
def update_budget_category(
    budget_id: UUID,
    budget_category_id: UUID,
    budget_category_update: BudgetCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật budget category"""
    updated_category = budget_crud.update_budget_category(
        db, 
        budget_category_id, 
        current_user.UserID, 
        budget_category_update
    )
    if not updated_category:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    # Kiểm tra budget_id có khớp không
    if updated_category.BudgetID != str(budget_id):
        raise HTTPException(status_code=400, detail="Budget category does not belong to this budget")
    
    return updated_category

@router.delete("/{budget_id}/categories/{budget_category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_category(
    budget_id: UUID,
    budget_category_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Xóa budget category"""
    # Kiểm tra budget category có tồn tại và thuộc về budget này không
    budget_category = budget_crud.get_budget_category(db, budget_category_id, current_user.UserID)
    if not budget_category:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    if budget_category.BudgetID != str(budget_id):
        raise HTTPException(status_code=400, detail="Budget category does not belong to this budget")
    
    success = budget_crud.delete_budget_category(db, budget_category_id, current_user.UserID)
    if not success:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    return None

# ==================== BUDGET WITH CATEGORIES ENDPOINTS ====================

@router.get("/{budget_id}/with-categories", response_model=BudgetWithCategories)
def get_budget_with_categories(
    budget_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy budget kèm theo danh sách categories"""
    # Lấy budget
    budget = budget_crud.get_budget(db, budget_id, current_user.UserID)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Lấy budget categories
    categories = budget_crud.get_budget_categories_by_budget(db, budget_id, current_user.UserID)
    
    # Tính tổng allocated và spent
    total_allocated = sum(cat.allocated_amount for cat in categories)
    total_spent = sum(cat.spent_amount for cat in categories)
    
    return BudgetWithCategories(
        budget_id=UUID(budget.BudgetID),
        user_id=UUID(budget.UserID),
        budget_name=budget.BudgetName,
        budget_type=budget.BudgetType,
        amount=budget.Amount,
        period_start=budget.PeriodStart,
        period_end=budget.PeriodEnd,
        auto_adjust=budget.AutoAdjust,
        include_income=budget.IncludeIncome,
        alert_threshold=budget.AlertThreshold,
        is_active=budget.IsActive,
        created_at=budget.CreatedAt,
        updated_at=budget.UpdatedAt,
        budget_categories=categories,
        total_allocated=total_allocated,
        total_spent=total_spent
    )

@router.post("/with-categories", response_model=BudgetWithCategories, status_code=status.HTTP_201_CREATED)
def create_budget_with_categories(
    budget_data: BudgetCreateWithCategories,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tạo budget kèm theo categories"""
    user_id = current_user.UserID
    
    try:
        # Tạo budget
        budget = budget_crud.create_budget(db, user_id, budget_data.budget)
        
        # Tạo budget categories
        categories = []
        for cat_data in budget_data.categories:
            cat_data.budget_id = UUID(budget.BudgetID)
            category = budget_crud.create_budget_category(db, user_id, cat_data)
            categories.append(category)
        
        # Lấy budget categories detail
        categories_detail = budget_crud.get_budget_categories_by_budget(db, UUID(budget.BudgetID), user_id)
        
        # Tính tổng
        total_allocated = sum(cat.allocated_amount for cat in categories_detail)
        total_spent = sum(cat.spent_amount for cat in categories_detail)
        
        return BudgetWithCategories(
            budget_id=UUID(budget.BudgetID),
            user_id=UUID(budget.UserID),
            budget_name=budget.BudgetName,
            budget_type=budget.BudgetType,
            amount=budget.Amount,
            period_start=budget.PeriodStart,
            period_end=budget.PeriodEnd,
            auto_adjust=budget.AutoAdjust,
            include_income=budget.IncludeIncome,
            alert_threshold=budget.AlertThreshold,
            is_active=budget.IsActive,
            created_at=budget.CreatedAt,
            updated_at=budget.UpdatedAt,
            budget_categories=categories_detail,
            total_allocated=total_allocated,
            total_spent=total_spent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== BUDGET ALERT ENDPOINTS ====================

@router.get("/alerts/", response_model=List[BudgetAlertResponse])
def get_user_budget_alerts(
    is_read: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách budget alerts của user"""
    return budget_crud.get_budget_alerts_by_user(
        db, 
        current_user.UserID, 
        is_read, 
        skip, 
        limit
    )

@router.put("/alerts/{alert_id}/mark-read", status_code=status.HTTP_204_NO_CONTENT)
def mark_alert_as_read(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Đánh dấu alert đã đọc"""
    success = budget_crud.mark_alert_as_read(db, alert_id, current_user.UserID)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return None

# ==================== UTILITY ENDPOINTS ====================

@router.get("/current/active", response_model=List[BudgetSummary])
def get_current_active_budgets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách budgets đang active trong kỳ hiện tại"""
    from datetime import date
    
    budgets = budget_crud.get_budgets_by_user(db, current_user.UserID, is_active=True)
    current_date = date.today()
    
    current_budgets = []
    for budget in budgets:
        if budget.PeriodStart <= current_date <= budget.PeriodEnd:
            summary = budget_crud.get_budget_summary(db, UUID(budget.BudgetID), current_user.UserID)
            if summary:
                current_budgets.append(summary)
    
    return current_budgets