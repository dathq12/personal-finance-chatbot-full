# crud/category_crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID
from typing import List, Optional, Dict, Any
from models.category import Category, UserCategory
from schemas.category_schema import CategoryCreate, CategoryUpdate, UserCategoryCreate, UserCategoryUpdate
import uuid

# ==================== CATEGORY CRUD ====================

def create_category(db: Session, category: CategoryCreate) -> Category:
    """Tạo danh mục mới"""
    category_data = category.dict()
    category_data['CategoryID'] = str(uuid.uuid4())
    
    # Convert field names to match database
    db_category = Category(
        CategoryID=category_data['CategoryID'],
        CategoryName=category_data['category_name'],
        CategoryType=category_data['category_type'],
        ParentCategoryID=category_data.get('parent_category_id'),
        Description=category_data.get('description'),
        Icon=category_data.get('icon'),
        Color=category_data.get('color'),
        IsDefault=category_data.get('is_default', False),
        SortOrder=category_data.get('sort_order', 0)
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: UUID) -> Optional[Category]:
    """Lấy danh mục theo ID"""
    return db.query(Category).filter(Category.CategoryID == str(category_id)).first()

def get_category_with_children(db: Session, category_id: UUID) -> Optional[Category]:
    """Lấy danh mục với các danh mục con"""
    return db.query(Category).options(
        joinedload(Category.children)
    ).filter(Category.CategoryID == str(category_id)).first()

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    parent_id: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: str = "sort_order",
    sort_order: str = "asc"
) -> List[Category]:
    """Lấy danh sách danh mục với các bộ lọc"""
    query = db.query(Category)
    
    # Apply filters
    if category_type:
        query = query.filter(Category.CategoryType == category_type)
    
    if is_active is not None:
        query = query.filter(Category.IsActive == is_active)
    
    if parent_id:
        query = query.filter(Category.ParentCategoryID == str(parent_id))
    elif parent_id is False:  # Get root categories only
        query = query.filter(Category.ParentCategoryID.is_(None))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Category.CategoryName.ilike(search_term),
                Category.Description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(desc(getattr(Category, _get_sort_column(sort_by))))
    else:
        query = query.order_by(asc(getattr(Category, _get_sort_column(sort_by))))
    
    return query.offset(skip).limit(limit).all()

def get_categories_count(
    db: Session,
    category_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    parent_id: Optional[UUID] = None,
    search: Optional[str] = None
) -> int:
    """Đếm số lượng danh mục"""
    query = db.query(Category)
    
    if category_type:
        query = query.filter(Category.CategoryType == category_type)
    
    if is_active is not None:
        query = query.filter(Category.IsActive == is_active)
    
    if parent_id:
        query = query.filter(Category.ParentCategoryID == str(parent_id))
    elif parent_id is False:
        query = query.filter(Category.ParentCategoryID.is_(None))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Category.CategoryName.ilike(search_term),
                Category.Description.ilike(search_term)
            )
        )
    
    return query.count()

def get_category_tree(db: Session, category_type: Optional[str] = None) -> List[Category]:
    """Lấy cây danh mục (chỉ danh mục gốc với con)"""
    query = db.query(Category).options(
        joinedload(Category.children)
    ).filter(Category.ParentCategoryID.is_(None))
    
    if category_type:
        query = query.filter(Category.CategoryType == category_type)
    
    return query.order_by(Category.SortOrder).all()

def update_category(db: Session, category_id: UUID, updates: CategoryUpdate) -> Optional[Category]:
    """Cập nhật danh mục"""
    db_category = db.query(Category).filter(Category.CategoryID == str(category_id)).first()
    
    if not db_category:
        return None
    
    update_data = updates.dict(exclude_unset=True)
    field_mapping = {
        'category_name': 'CategoryName',
        'category_type': 'CategoryType',
        'parent_category_id': 'ParentCategoryID',
        'description': 'Description',
        'icon': 'Icon',
        'color': 'Color',
        'is_default': 'IsDefault',
        'is_active': 'IsActive',
        'sort_order': 'SortOrder'
    }
    
    for field, value in update_data.items():
        if field in field_mapping:
            db_field = field_mapping[field]
            if field == 'parent_category_id' and value:
                value = str(value)
            setattr(db_category, db_field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: UUID, soft_delete: bool = True) -> bool:
    """Xóa danh mục (soft delete hoặc hard delete)"""
    db_category = db.query(Category).filter(Category.CategoryID == str(category_id)).first()
    
    if not db_category:
        return False
    
    if soft_delete:
        db_category.IsActive = False
        db.commit()
    else:
        db.delete(db_category)
        db.commit()
    
    return True

# ==================== USER CATEGORY CRUD ====================

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

# ==================== HELPER FUNCTIONS ====================

def _get_sort_column(sort_by: str) -> str:
    """Map sort field names to database column names"""
    sort_mapping = {
        'category_name': 'CategoryName',
        'category_type': 'CategoryType',
        'sort_order': 'SortOrder',
        'created_at': 'CreatedAt',
        'is_active': 'IsActive'
    }
    return sort_mapping.get(sort_by, 'SortOrder')

def get_categories_by_type(db: Session, category_type: str) -> List[Category]:
    """Lấy danh mục theo loại"""
    return db.query(Category).filter(
        and_(
            Category.CategoryType == category_type,
            Category.IsActive == True
        )
    ).order_by(Category.SortOrder).all()

def get_default_categories(db: Session) -> List[Category]:
    """Lấy danh mục mặc định"""
    return db.query(Category).filter(
        and_(
            Category.IsDefault == True,
            Category.IsActive == True
        )
    ).order_by(Category.SortOrder).all()