# budget_crud.py
# crud/budget_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from uuid import UUID
from typing import List, Optional, Dict, Any
from models.budget import Budget, BudgetAlert, BudgetCategory
from models.category import UserCategory, Category
from schemas.budget_schema import (
    BudgetCreate, BudgetUpdate, BudgetCategoryCreate, BudgetCategoryUpdate,
    BudgetAlertCreate, BudgetAlertUpdate, BudgetSummary, BudgetCategoryDetail
)
from decimal import Decimal
from datetime import datetime, date
import uuid
from fastapi import HTTPException

# ==================== BUDGET CRUD ====================

def get_budget(db: Session, budget_id: UUID, user_id: UUID) -> Optional[Budget]:
    """Lấy budget theo ID và user ID"""
    return db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id,
        Budget.IsActive == True
    ).first()

def get_budgets_by_user(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    budget_type: Optional[str] = None
) -> List[Budget]:
    """Lấy danh sách budgets của user"""
    query = db.query(Budget).filter(Budget.UserID == user_id)
    
    if is_active is not None:
        query = query.filter(Budget.IsActive == is_active)
    
    if budget_type:
        query = query.filter(Budget.BudgetType == budget_type)
    
    return query.order_by(Budget.CreatedAt.desc()).offset(skip).limit(limit).all()

def get_budgets_count(
    db: Session,
    user_id: UUID,
    is_active: Optional[bool] = None,
    budget_type: Optional[str] = None
) -> int:
    """Đếm số lượng budgets của user"""
    query = db.query(Budget).filter(Budget.UserID == user_id)
    
    if is_active is not None:
        query = query.filter(Budget.IsActive == is_active)
    
    if budget_type:
        query = query.filter(Budget.BudgetType == budget_type)
    
    return query.count()

def create_budget(db: Session, user_id: UUID, budget: BudgetCreate) -> Budget:
    """Tạo budget mới"""
    db_budget = Budget(
        # BudgetID=str(uuid.uuid4()),
        UserID=user_id,
        BudgetName=budget.budget_name,
        BudgetType=budget.budget_type.value,
        Amount=budget.amount,
        PeriodStart=budget.period_start,
        PeriodEnd=budget.period_end,
        AutoAdjust=budget.auto_adjust,
        IncludeIncome=budget.include_income,
        AlertThreshold=budget.alert_threshold
    )
    
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(
    db: Session,
    budget_id: UUID,
    user_id: UUID,
    updates: BudgetUpdate
) -> Optional[Budget]:
    """Cập nhật budget"""
    db_budget = db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id
    ).first()
    
    if not db_budget:
        return None
    
    update_data = updates.model_dump(exclude_unset=True)
    field_mapping = {
        'budget_name': 'BudgetName',
        'amount': 'Amount',
        'period_start': 'PeriodStart',
        'period_end': 'PeriodEnd',
        'auto_adjust': 'AutoAdjust',
        'include_income': 'IncludeIncome',
        'alert_threshold': 'AlertThreshold',
        'is_active': 'IsActive'
    }
    
    for field, value in update_data.items():
        if field in field_mapping:
            setattr(db_budget, field_mapping[field], value)
    
    db_budget.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: UUID, user_id: UUID) -> bool:
    """Xóa budget (soft delete)"""
    db_budget = db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id
    ).first()
    
    if not db_budget:
        return False
    
    db_budget.IsActive = False
    db_budget.UpdatedAt = datetime.utcnow()
    db.commit()
    
    return True

def hard_delete_budget(db: Session, budget_id: UUID, user_id: UUID) -> bool:
    """Xóa hoàn toàn budget và các dữ liệu liên quan"""
    db_budget = db.query(Budget).filter(
        Budget.BudgetID == budget_id,
        Budget.UserID == user_id
    ).first()
    
    if not db_budget:
        return False
    
    # Xóa budget categories
    db.query(BudgetCategory).filter(BudgetCategory.BudgetID == budget_id).delete()
    
    # Xóa budget alerts  
    db.query(BudgetAlert).filter(BudgetAlert.BudgetID == budget_id).delete()
    
    # Xóa budget
    db.delete(db_budget)
    db.commit()
    
    return True

def get_budget_summary(db: Session, budget_id: UUID, user_id: UUID) -> Optional[BudgetSummary]:
    """Lấy tóm tắt budget với thông tin chi tiêu"""
    budget = get_budget(db, budget_id, user_id)
    if not budget:
        return None
    
    # Tính tổng chi tiêu từ budget categories
    spent_amount = db.query(func.sum(BudgetCategory.SpentAmount)).filter(
        BudgetCategory.BudgetID == budget_id
    ).scalar() or Decimal('0.00')
    
    remaining_amount = budget.Amount - spent_amount
    percentage_used = (spent_amount / budget.Amount * 100) if budget.Amount > 0 else Decimal('0.00')
    
    return BudgetSummary(
        budget_id=UUID(budget.BudgetID),
        budget_name=budget.BudgetName,
        amount=budget.Amount,
        spent_amount=spent_amount,
        remaining_amount=remaining_amount,
        percentage_used=percentage_used,
        budget_type=budget.BudgetType,
        period_start=budget.PeriodStart,
        period_end=budget.PeriodEnd,
        is_active=budget.IsActive
    )

# ==================== BUDGET CATEGORY CRUD ====================

def get_budget_category(
    db: Session,
    budget_category_id: UUID,
    user_id: UUID
) -> Optional[BudgetCategory]:
    """Lấy budget category theo ID"""
    return db.query(BudgetCategory).join(Budget).filter(
        BudgetCategory.BudgetCategoryID == str(budget_category_id),
        Budget.UserID == user_id
    ).first()

def get_budget_categories_by_budget(
    db: Session,
    budget_id: UUID,
    user_id: UUID
) -> List[BudgetCategoryDetail]:
    """Lấy danh sách budget categories theo budget ID"""
    results = (
        db.query(BudgetCategory, UserCategory, Category)
        .join(Budget, BudgetCategory.BudgetID == Budget.BudgetID)
        .join(UserCategory, BudgetCategory.UserCategoryID == UserCategory.UserCategoryID)
        .join(Category, UserCategory.CategoryID == Category.CategoryID, isouter=True)
        .filter(
            Budget.BudgetID == budget_id,
            Budget.UserID == user_id
        )
        .all()
    )
    
    budget_categories = []
    for budget_cat, user_cat, category in results:
        # Xác định display name
        if user_cat.CustomName:
            display_name = user_cat.CustomName
        elif category:
            display_name = category.CategoryName
        else:
            display_name = "Unknown Category"
        
        remaining_amount = budget_cat.AllocatedAmount - budget_cat.SpentAmount
        percentage_used = (
            (budget_cat.SpentAmount / budget_cat.AllocatedAmount * 100) 
            if budget_cat.AllocatedAmount > 0 else Decimal('0.00')
        )
        
        budget_categories.append(BudgetCategoryDetail(
            budget_category_id=UUID(budget_cat.BudgetCategoryID),
            budget_id=UUID(budget_cat.BudgetID),
            user_category_id=UUID(budget_cat.UserCategoryID),
            allocated_amount=budget_cat.AllocatedAmount,
            spent_amount=budget_cat.SpentAmount,
            category_display_name=display_name,
            remaining_amount=remaining_amount,
            percentage_used=percentage_used,
            created_at=budget_cat.CreatedAt,
            updated_at=budget_cat.UpdatedAt
        ))
    
    return budget_categories

def create_budget_category(
    db: Session,
    user_id: UUID,
    budget_category: BudgetCategoryCreate
) -> BudgetCategory:
    """Tạo budget category"""
    # Kiểm tra budget có thuộc về user không
    budget = get_budget(db, budget_category.budget_id, user_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Kiểm tra user category có tồn tại không
    user_category = db.query(UserCategory).filter(
        UserCategory.UserCategoryID == str(budget_category.user_category_id),
        UserCategory.UserID == user_id
    ).first()
    
    if not user_category:
        raise HTTPException(status_code=404, detail="User category not found")
    
    # Kiểm tra đã tồn tại chưa
    existing = db.query(BudgetCategory).filter(
        BudgetCategory.BudgetID == str(budget_category.budget_id),
        BudgetCategory.UserCategoryID == str(budget_category.user_category_id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget category already exists for this budget and category"
        )
    
    db_budget_category = BudgetCategory(
        BudgetCategoryID=str(uuid.uuid4()),
        BudgetID=str(budget_category.budget_id),
        UserCategoryID=str(budget_category.user_category_id),
        AllocatedAmount=budget_category.allocated_amount
    )
    
    db.add(db_budget_category)
    db.commit()
    db.refresh(db_budget_category)
    return db_budget_category

def update_budget_category(
    db: Session,
    budget_category_id: UUID,
    user_id: UUID,
    updates: BudgetCategoryUpdate
) -> Optional[BudgetCategory]:
    """Cập nhật budget category"""
    db_budget_category = get_budget_category(db, budget_category_id, user_id)
    
    if not db_budget_category:
        return None
    
    update_data = updates.model_dump(exclude_unset=True)
    field_mapping = {
        'allocated_amount': 'AllocatedAmount'
    }
    
    for field, value in update_data.items():
        if field in field_mapping:
            setattr(db_budget_category, field_mapping[field], value)
    
    db_budget_category.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(db_budget_category)
    return db_budget_category

def delete_budget_category(
    db: Session,
    budget_category_id: UUID,
    user_id: UUID
) -> bool:
    """Xóa budget category"""
    db_budget_category = get_budget_category(db, budget_category_id, user_id)
    
    if not db_budget_category:
        return False
    
    db.delete(db_budget_category)
    db.commit()
    return True

# ==================== BUDGET ALERT CRUD ====================

def create_budget_alert(db: Session, alert: BudgetAlertCreate) -> BudgetAlert:
    """Tạo budget alert"""
    db_alert = BudgetAlert(
        AlertID=str(uuid.uuid4()),
        BudgetID=str(alert.budget_id),
        UserID=str(alert.user_id),
        AlertType=alert.alert_type.value,
        CurrentAmount=alert.current_amount,
        BudgetAmount=alert.budget_amount,
        PercentageUsed=alert.percentage_used,
        Message=alert.message
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_budget_alerts_by_user(
    db: Session,
    user_id: UUID,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[BudgetAlert]:
    """Lấy danh sách alerts của user"""
    query = db.query(BudgetAlert).filter(BudgetAlert.UserID == user_id)
    
    if is_read is not None:
        query = query.filter(BudgetAlert.IsRead == is_read)
    
    return query.order_by(BudgetAlert.CreatedAt.desc()).offset(skip).limit(limit).all()

def mark_alert_as_read(db: Session, alert_id: UUID, user_id: UUID) -> bool:
    """Đánh dấu alert đã đọc"""
    db_alert = db.query(BudgetAlert).filter(
        BudgetAlert.AlertID == str(alert_id),
        BudgetAlert.UserID == user_id
    ).first()
    
    if not db_alert:
        return False
    
    db_alert.IsRead = True
    db.commit()
    return True