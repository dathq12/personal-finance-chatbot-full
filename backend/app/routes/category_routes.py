# routers/category_router.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from schemas.category_schema import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse,
    UserCategoryCreate, UserCategoryUpdate, UserCategoryResponse, UserCategoryListResponse,
    CategoryWithChildren
)
from crud import category_crud

# Create router
router = APIRouter(prefix="/categories", tags=["categories"])

# ==================== CATEGORY ENDPOINTS ====================

@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Tạo danh mục mới"""
    try:
        return category_crud.create_category(db=db, category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID = Path(..., description="ID của danh mục"),
    db: Session = Depends(get_db)
):
    """Lấy thông tin danh mục theo ID"""
    category = category_crud.get_category(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/{category_id}/with-children", response_model=CategoryWithChildren)
async def get_category_with_children(
    category_id: UUID = Path(..., description="ID của danh mục"),
    db: Session = Depends(get_db)
):
    """Lấy danh mục kèm các danh mục con"""
    category = category_crud.get_category_with_children(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1, description="Số trang"),
    per_page: int = Query(20, ge=1, le=100, description="Số item mỗi trang"),
    category_type: Optional[str] = Query(None, description="Loại danh mục"),
    is_active: Optional[bool] = Query(None, description="Trạng thái hoạt động"),
    parent_id: Optional[UUID] = Query(None, description="ID danh mục cha"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc mô tả"),
    sort_by: str = Query("sort_order", description="Sắp xếp theo trường"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Thứ tự sắp xếp"),
    db: Session = Depends(get_db)
):
    """Lấy danh sách danh mục với phân trang và bộ lọc"""
    skip = (page - 1) * per_page
    
    categories = category_crud.get_categories(
        db=db,
        skip=skip,
        limit=per_page,
        category_type=category_type,
        is_active=is_active,
        parent_id=parent_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = category_crud.get_categories_count(
        db=db,
        category_type=category_type,
        is_active=is_active,
        parent_id=parent_id,
        search=search
    )
    
    return CategoryListResponse(
        categories=categories,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/tree/all", response_model=List[CategoryWithChildren])
async def get_category_tree(
    category_type: Optional[str] = Query(None, description="Loại danh mục"),
    db: Session = Depends(get_db)
):
    """Lấy cây danh mục (danh mục gốc với các con)"""
    return category_crud.get_category_tree(db=db, category_type=category_type)

@router.get("/type/{category_type}", response_model=List[CategoryResponse])
async def get_categories_by_type(
    category_type: str = Path(..., description="Loại danh mục"),
    db: Session = Depends(get_db)
):
    """Lấy danh mục theo loại"""
    return category_crud.get_categories_by_type(db=db, category_type=category_type)

@router.get("/defaults/all", response_model=List[CategoryResponse])
async def get_default_categories(
    db: Session = Depends(get_db)
):
    """Lấy tất cả danh mục mặc định"""
    return category_crud.get_default_categories(db=db)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID = Path(..., description="ID của danh mục"),
    updates: CategoryUpdate = ...,
    db: Session = Depends(get_db)
):
    """Cập nhật danh mục"""
    category = category_crud.update_category(db=db, category_id=category_id, updates=updates)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID = Path(..., description="ID của danh mục"),
    permanent: bool = Query(False, description="Xóa vĩnh viễn (true) hoặc soft delete (false)"),
    db: Session = Depends(get_db)
):
    """Xóa danh mục"""
    success = category_crud.delete_category(db=db, category_id=category_id, soft_delete=not permanent)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return None

# ==================== USER CATEGORY ENDPOINTS ====================

@router.post("/user-categories/", response_model=UserCategoryResponse, status_code=201)
async def create_user_category(
    user_category: UserCategoryCreate,
    db: Session = Depends(get_db)
):
    """Tạo liên kết user-category"""
    try:
        return category_crud.create_user_category(db=db, user_category=user_category)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user-categories/{user_category_id}", response_model=UserCategoryResponse)
async def get_user_category(
    user_category_id: UUID = Path(..., description="ID của user category"),
    db: Session = Depends(get_db)
):
    """Lấy thông tin user category theo ID"""
    user_category = category_crud.get_user_category(db=db, user_category_id=user_category_id)
    if not user_category:
        raise HTTPException(status_code=404, detail="User category not found")
    return user_category

@router.get("/users/{user_id}/categories", response_model=UserCategoryListResponse)
async def get_user_categories(
    user_id: UUID = Path(..., description="ID của user"),
    page: int = Query(1, ge=1, description="Số trang"),
    per_page: int = Query(20, ge=1, le=100, description="Số item mỗi trang"),
    is_active: Optional[bool] = Query(None, description="Trạng thái hoạt động"),
    category_type: Optional[str] = Query(None, description="Loại danh mục"),
    db: Session = Depends(get_db)
):
    """Lấy danh sách user categories theo user"""
    skip = (page - 1) * per_page
    
    user_categories = category_crud.get_user_categories_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=per_page,
        is_active=is_active,
        category_type=category_type
    )
    
    total = category_crud.get_user_categories_count(
        db=db,
        user_id=user_id,
        is_active=is_active,
        category_type=category_type
    )
    
    return UserCategoryListResponse(
        user_categories=user_categories,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/users/{user_id}/categories/{category_id}", response_model=UserCategoryResponse)
async def get_user_category_by_user_and_category(
    user_id: UUID = Path(..., description="ID của user"),
    category_id: UUID = Path(..., description="ID của category"),
    db: Session = Depends(get_db)
):
    """Lấy user category theo user và category"""
    user_category = category_crud.get_user_category_by_user_and_category(
        db=db, user_id=user_id, category_id=category_id
    )
    if not user_category:
        raise HTTPException(status_code=404, detail="User category not found")
    return user_category

@router.put("/user-categories/{user_category_id}", response_model=UserCategoryResponse)
async def update_user_category(
    user_category_i