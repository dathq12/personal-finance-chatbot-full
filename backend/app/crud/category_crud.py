# crud/category_crud.py - Updated version
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID
from typing import List, Optional, Dict, Any
from models.category import Category, UserCategory
from schemas.category_schema import CategoryCreate, CategoryUpdate, UserCategoryCreate, UserCategoryUpdate, CategoryDisplayResponse
import uuid
from fastapi import HTTPException
# ==================== CATEGORY CRUD ====================

def get_category(db: Session, category_id: UUID) -> Optional[Category]:
    """Lấy category theo ID"""
    return db.query(Category).filter(
        Category.CategoryID == str(category_id),
        Category.IsActive == True
    ).first()

def get_categories_by_type(
    db: Session, 
    category_type: str,
    skip: int = 0,
    limit: int = 100
) -> List[Category]:
    """Lấy danh sách categories theo type"""
    return db.query(Category).filter(
        Category.CategoryType == category_type,
        Category.IsActive == True
    ).order_by(Category.SortOrder, Category.CategoryName).offset(skip).limit(limit).all()

def create_category(db: Session, category: CategoryCreate) -> Category:
    """Tạo category mới"""
    db_category = Category(
        CategoryID=uuid.uuid4(),
        CategoryName=category.category_name,
        CategoryType=category.category_type,
        ParentCategoryID=category.parent_category_id if category.parent_category_id else None,
        Description=category.description,
        Icon=category.icon,
        Color=category.color,
        IsDefault=category.is_default,
        SortOrder=category.sort_order or 0
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# ==================== USER CATEGORY CRUD ====================

def get_all_category_display_names(db: Session, user_id: UUID) -> List[CategoryDisplayResponse]:
    """Lấy toàn bộ tên danh mục hiển thị của một người, bao gồm:
       - Category mặc định của hệ thống (dù user chưa dùng)
       - UserCategory liên kết
       - UserCategory custom"""
    
    # Lấy tất cả Category mặc định
    system_categories = db.query(Category).filter(Category.IsActive == True).all()

    # Lấy toàn bộ UserCategory của user
    user_categories = db.query(UserCategory).filter(
        UserCategory.UserID == user_id,
        UserCategory.IsActive == True
    ).all()
    user_category_map = {uc.CategoryID: uc for uc in user_categories if uc.CategoryID}

    display_categories = []

    # Thêm tất cả category mặc định (liên kết hoặc chưa dùng)
    for cat in system_categories:
        if cat.CategoryID in user_category_map:
            uc = user_category_map[cat.CategoryID]
            display_name = uc.CustomName if uc.CustomName else cat.CategoryName
            is_custom = bool(uc.CustomName)
            user_category_id = uc.UserCategoryID
        else:
            display_name = cat.CategoryName
            is_custom = False
            user_category_id = None

        display_categories.append(CategoryDisplayResponse(
            display_name=display_name,
            category_type=cat.CategoryType,
            user_category_id=user_category_id,
            category_id=cat.CategoryID,
            is_custom=is_custom
        ))

    # Thêm user categories hoàn toàn custom
    custom_only = [uc for uc in user_categories if uc.CategoryID is None]
    for uc in custom_only:
        display_categories.append(CategoryDisplayResponse(
            display_name=uc.CustomName,
            category_type=uc.CategoryType,
            user_category_id=uc.UserCategoryID,
            category_id=None,
            is_custom=True
        ))

    # Sắp xếp
    display_categories.sort(key=lambda x: (x.category_type, x.display_name))
    return display_categories


def get_category_display_names_by_type(
    db: Session,
    user_id: UUID,
    category_type: str
) -> List[CategoryDisplayResponse]:
    """Lấy toàn bộ tên danh mục hiển thị theo loại, bao gồm:
       - Category mặc định của hệ thống (dù user chưa dùng)
       - UserCategory liên kết
       - UserCategory custom"""
    
    # Lấy tất cả Category mặc định theo loại
    system_categories = db.query(Category).filter(
        Category.IsActive == True,
        Category.CategoryType == category_type
    ).all()

    # Lấy toàn bộ UserCategory của user theo loại
    user_categories = db.query(UserCategory).filter(
        UserCategory.UserID == user_id,
        UserCategory.IsActive == True,
        UserCategory.CategoryType == category_type
    ).all()
    user_category_map = {uc.CategoryID: uc for uc in user_categories if uc.CategoryID}

    display_categories = []

    # Thêm tất cả category mặc định (liên kết hoặc chưa dùng)
    for cat in system_categories:
        if cat.CategoryID in user_category_map:
            uc = user_category_map[cat.CategoryID]
            display_name = uc.CustomName if uc.CustomName else cat.CategoryName
            is_custom = bool(uc.CustomName)
            user_category_id = uc.UserCategoryID
        else:
            display_name = cat.CategoryName
            is_custom = False
            user_category_id = None

        display_categories.append(CategoryDisplayResponse(
            display_name=display_name,
            category_type=cat.CategoryType,
            user_category_id=user_category_id,
            category_id=cat.CategoryID,
            is_custom=is_custom
        ))

    # Thêm user categories hoàn toàn custom
    custom_only = [uc for uc in user_categories if uc.CategoryID is None]
    for uc in custom_only:
        display_categories.append(CategoryDisplayResponse(
            display_name=uc.CustomName,
            category_type=uc.CategoryType,
            user_category_id=uc.UserCategoryID,
            category_id=None,
            is_custom=True
        ))

    # Sắp xếp
    display_categories.sort(key=lambda x: x.display_name)
    return display_categories


def get_category_display_name(db: Session, user_category_id: UUID) -> str:
    """Get the display name of a user category"""
    user_category = (
        db.query(UserCategory)
        .filter(UserCategory.UserCategoryID == user_category_id)
        .first()
    )
    
    if not user_category:
        return "Unknown Category"
    
    # Nếu là custom category hoàn toàn
    if not user_category.CategoryID:
        return user_category.CustomName or "Unknown Category"
    
    # Nếu có liên kết với category gốc
    category = (
        db.query(Category)
        .filter(Category.CategoryID == user_category.CategoryID)
        .first()
    )
    
    if not category:
        return user_category.CustomName or "Unknown Category"
    
    return user_category.CustomName if user_category.CustomName else category.CategoryName

def create_user_category(db: Session, user_id: UUID, user_category: UserCategoryCreate) -> UserCategory:
    """Tạo user category (có thể là custom hoàn toàn hoặc dựa trên category gốc)"""
    

    # Nếu có category_id → category dựa trên gốc
    if user_category.category_id:
        existing = get_user_category_by_user_and_category(
            db, user_id, user_category.category_id
        )
        if existing:
            if not existing.IsActive:
                existing.IsActive = True
                existing.CustomName = user_category.custom_name
                db.commit()
                db.refresh(existing)
                return existing
            else:
                raise HTTPException(
                    status_code=400,
                    detail="User category already exists and is active"
                )

        category = get_category(db, user_category.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category.CategoryType != user_category.category_type:
            raise HTTPException(status_code=400, detail="Category type mismatch")

    else:
        # Custom category hoàn toàn - THÊM FILTER CHO CategoryType
        existing_custom = (
            db.query(UserCategory)
            .filter(
                UserCategory.UserID == user_id,
                UserCategory.CategoryID.is_(None),
                UserCategory.CustomName == user_category.custom_name,
                UserCategory.CategoryType == user_category.category_type  # THÊM DÒNG NÀY
            )
            .first()
        )

        if existing_custom:
            if not existing_custom.IsActive:
                existing_custom.IsActive = True
                existing_custom.CustomName = user_category.custom_name
                db.commit()
                db.refresh(existing_custom)
                return existing_custom
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Custom category with this name already exists and is active"
                )

    # Tạo mới
    db_user_category = UserCategory(
        UserID=user_id,
        CategoryID=user_category.category_id if user_category.category_id else None,
        CustomName=user_category.custom_name,
        CategoryType=user_category.category_type
    )

    db.add(db_user_category)
    db.commit()
    db.refresh(db_user_category)
    return db_user_category

def get_user_category(
    db: Session, 
    user_id: UUID, 
    user_category_id: UUID
):
    """Lấy user category theo ID và User ID"""
    return (
        db.query(UserCategory, Category)
        .join(Category, UserCategory.CategoryID == Category.CategoryID, isouter=True)  # LEFT JOIN
        .filter(
            UserCategory.UserCategoryID == user_category_id,
            UserCategory.UserID == user_id
        )
        .first()
    )




def get_user_categories_by_user(
    db: Session, 
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    category_type: Optional[str] = None
):
    """Lấy danh sách user categories theo user"""
    query = db.query(UserCategory, Category).join(
        Category, UserCategory.CategoryID == Category.CategoryID, isouter=True  # Sửa INNER → LEFT JOIN
    ).filter(UserCategory.UserID == user_id)
    
    if is_active is not None:
        query = query.filter(UserCategory.IsActive == is_active)
    
    if category_type:
        # Với custom category (CategoryID NULL), filter theo Category.CategoryType sẽ bỏ mất chúng
        query = query.filter(
            (Category.CategoryType == category_type) |
            ((UserCategory.CategoryID.is_(None)) & (UserCategory.CategoryType == category_type))
        )
    
    return query.order_by(UserCategory.CreatedAt.desc()) \
            .offset(skip) \
            .limit(limit) \
            .all()




def get_user_categories_count(
    db: Session,
    user_id: UUID,
    is_active: Optional[bool] = None,
    category_type: Optional[str] = None
) -> int:
    """Đếm số lượng user categories"""
    query = db.query(UserCategory).filter(UserCategory.UserID == user_id)
    
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
            UserCategory.UserID == user_id,
            UserCategory.CategoryID == category_id
        )
    ).first()

def update_user_category(
    db: Session, 
    user_category_id: UUID, 
    updates: UserCategoryUpdate
) -> Optional[UserCategory]:
    """Cập nhật user category"""
    db_user_category = db.query(UserCategory).filter(
        UserCategory.UserCategoryID == user_category_id
    ).first()
    
    if not db_user_category:
        return None
    
    update_data = updates.model_dump(exclude_unset=True)
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

def delete_user_category(db: Session,user_id: UUID, user_category_id: UUID) -> bool:
    """Xóa user category"""
    db_user_category = db.query(UserCategory).filter(
        UserCategory.UserCategoryID == user_category_id,
        UserCategory.UserID == user_id
    ).first()
    
    if not db_user_category:
        return False
    

    db.delete(db_user_category)
    db.commit()
    
    return True

def get_user_category_id_by_display_name(
    db: Session, 
    user_id: UUID, 
    display_name: str,
    transaction_type: str
) -> Optional[UUID]:
    """Get user category ID by display name and transaction type"""
    
    # Tìm trong user categories có liên kết với category gốc
    linked_result = (
        db.query(UserCategory)
        .join(Category, UserCategory.CategoryID == Category.CategoryID)
        .filter(
            UserCategory.UserID == user_id,
            UserCategory.IsActive == True,
            Category.CategoryType == transaction_type,
            or_(
                UserCategory.CustomName == display_name,
                and_(
                    UserCategory.CustomName.is_(None), 
                    Category.CategoryName == display_name
                )
            )
        )
        .first()
    )
    
    if linked_result:
        return linked_result.UserCategoryID
    
    # Tìm trong user categories hoàn toàn tùy chỉnh
    custom_result = (
        db.query(UserCategory)
        .filter(
            UserCategory.UserID == user_id,
            UserCategory.CategoryID.is_(None),
            UserCategory.CategoryType == transaction_type,
            UserCategory.CustomName == display_name,
            UserCategory.IsActive == True
        )
        .first()
    )
    
    if custom_result:
        return custom_result.UserCategoryID
    
    # Nếu không tìm thấy, tìm trong category gốc và tạo user category mới
    category = (
        db.query(Category)
        .filter(
            Category.IsActive == True,
            Category.CategoryType == transaction_type,
            Category.CategoryName == display_name
        )
        .first()
    )
    
    if category:
        # Tạo user category mới cho user
        new_user_cat = UserCategory(
            UserID=user_id,
            CategoryID=category.CategoryID,
            CustomName=None,
            CategoryType=category.CategoryType,
            IsActive=True
        )
        db.add(new_user_cat)
        db.commit()
        db.refresh(new_user_cat)
        return new_user_cat.UserCategoryID
    
    return None