# crud/category_crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID
from typing import List, Optional, Dict, Any
from models.category import Category, UserCategory
from schemas.category_schema import CategoryCreate, CategoryUpdate, UserCategoryCreate, UserCategoryUpdate
import uuid

# ==================== CATEGORY CRUD ====================


# ==================== USER CATEGORY CRUD ====================

def get_all_category_display_names(db: Session, user_id: UUID) -> list[str]:
    """Lấy toàn bộ tên danh mục (custom hoặc mặc định) của một người"""
    results = (
        db.query(UserCategory, Category)
        .join(Category, UserCategory.CategoryID == Category.CategoryID)
        .filter(UserCategory.UserID == user_id, UserCategory.IsActive == True)
        .all()
    )
    
    display_names = []
    for user_category, category in results:
        display_names.append(user_category.CustomName if user_category.CustomName else category.CategoryName)
    
    return display_names

def get_category_display_name(db: Session, user_category_id: UUID) -> str:
    """Get the display name of a user category"""
    result = (
        db.query(UserCategory, Category)
        .join(Category, UserCategory.CategoryID == Category.CategoryID)
        .filter(UserCategory.UserCategoryID == user_category_id)
        .first()
    )
    if not result:
        return "Unknown Category"
    user_category, category = result
    return user_category.CustomName if user_category.CustomName else category.CategoryName



def create_user_category(db: Session, user_category: UserCategoryCreate) -> UserCategory:
    """Tạo liên kết user-category"""
    # Check if already exists
    existing = get_user_category_by_user_and_category(
        db, user_category.user_id, user_category.category_id
    )
    if existing:
        # If exists but inactive, reactivate it
        if not existing.IsActive:
            existing.IsActive = True
            existing.CustomName = user_category.custom_name
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise ValueError("User category already exists and is active")
    
    db_user_category = UserCategory(
        UserCategoryID=str(uuid.uuid4()),
        UserID=str(user_category.user_id),
        CategoryID=str(user_category.category_id),
        CustomName=user_category.custom_name
    )
    
    db.add(db_user_category)
    db.commit()
    db.refresh(db_user_category)
    return db_user_category

def get_user_category(db: Session, user_category_id: UUID) -> Optional[UserCategory]:
    """Lấy user category theo ID"""
    return db.query(UserCategory).options(
        joinedload(UserCategory.category)
    ).filter(UserCategory.UserCategoryID == str(user_category_id)).first()

def get_user_categories_by_user(
    db: Session, 
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    category_type: Optional[str] = None
) -> List[UserCategory]:
    """Lấy danh sách user categories theo user"""
    query = db.query(UserCategory).options(
        joinedload(UserCategory.category)
    ).filter(UserCategory.UserID == str(user_id))
    
    if is_active is not None:
        query = query.filter(UserCategory.IsActive == is_active)
    
    if category_type:
        query = query.join(Category).filter(Category.CategoryType == category_type)
    
    return query.offset(skip).limit(limit).all()

def get_user_categories_count(
    db: Session,
    user_id: UUID,
    is_active: Optional[bool] = None,
    category_type: Optional[str] = None
) -> int:
    """Đếm số lượng user categories"""
    query = db.query(UserCategory).filter(UserCategory.UserID == str(user_id))
    
    if is_active is not None:
        query = query.filter(UserCategory.IsActive == is_active)
    
    if category_type:
        query = query.join(Category).filter(Category.CategoryType == category_type)
    
    return query.count()

def get_user_category_by_user_and_category(
    db: Session, 
    user_id: UUID, 
    category_id: UUID
) -> Optional[UserCategory]:
    """Lấy user category theo user và category"""
    return db.query(UserCategory).filter(
        and_(
            UserCategory.UserID == str(user_id),
            UserCategory.CategoryID == str(category_id)
        )
    ).first()

def update_user_category(
    db: Session, 
    user_category_id: UUID, 
    updates: UserCategoryUpdate
) -> Optional[UserCategory]:
    """Cập nhật user category"""
    db_user_category = db.query(UserCategory).filter(
        UserCategory.UserCategoryID == str(user_category_id)
    ).first()
    
    if not db_user_category:
        return None
    
    update_data = updates.dict(exclude_unset=True)
    field_mapping = {
        'custom_name': 'CustomName',
        'is_active': 'IsActive'
    }
    
    for field, value in update_data.items():
        if field in field_mapping:
            setattr(db_user_category, field_mapping[field], value)
    
    db.commit()
    db.refresh(db_user_category)
    return db_user_category

def delete_user_category(db: Session, user_category_id: UUID, soft_delete: bool = True) -> bool:
    """Xóa user category"""
    db_user_category = db.query(UserCategory).filter(
        UserCategory.UserCategoryID == str(user_category_id)
    ).first()
    
    if not db_user_category:
        return False
    
    if soft_delete:
        db_user_category.IsActive = False
        db.commit()
    else:
        db.delete(db_user_category)
        db.commit()
    
    return True
