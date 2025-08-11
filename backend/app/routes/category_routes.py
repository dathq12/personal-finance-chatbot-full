# routers/category_router.py - Complete router
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from database import get_db
from schemas.category_schema import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse,
    UserCategoryCreate, UserCategoryUpdate, UserCategoryResponse, UserCategoryListResponse,
    CategoryDisplayListResponse
)
from crud import category_crud
from auth.auth_dependency import get_current_user

# Create router
router = APIRouter(
    prefix="/categories", 
    tags=["categories"],
    dependencies=[Depends(HTTPBearer())]
)

# ==================== CATEGORY ENDPOINTS ====================

@router.get("/types/{category_type}", response_model=CategoryListResponse)
async def get_categories_by_type(
    category_type: str = Path(..., description="Loại danh mục (income/expense)"),
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng tối đa"),
    db: Session = Depends(get_db)
):
    """Lấy danh sách categories theo loại"""
    categories = category_crud.get_categories_by_type(
        db=db, 
        category_type=category_type,
        skip=skip,
        limit=limit
    )
    
    return CategoryListResponse(
        categories=categories,
        total=len(categories)
    )

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tạo danh mục mới (chỉ admin)"""
    return category_crud.create_category(db=db, category=category)

# ==================== USER CATEGORY ENDPOINTS ====================

@router.post("/user-categories/", response_model=UserCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_user_category(
    user_category: UserCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Thêm danh mục cho user"""
    try:
        db_user_category = category_crud.create_user_category(
            db=db, 
            user_id=current_user.UserID, 
            user_category=user_category
        )
        
        # Lấy thông tin category để trả về (nếu có)
        category = None
        if db_user_category.CategoryID:
            category = category_crud.get_category(db, db_user_category.CategoryID)
        
        display_name = db_user_category.CustomName
        
        return UserCategoryResponse(
            user_category_id=db_user_category.UserCategoryID,
            user_id=db_user_category.UserID,
            category_id=db_user_category.CategoryID if db_user_category.CategoryID else None,
            custom_name=db_user_category.CustomName,
            category_type=db_user_category.CategoryType,
            is_active=db_user_category.IsActive,
            created_at=db_user_category.CreatedAt,
            category=CategoryResponse(
                category_id=category.CategoryID,
                category_name=category.CategoryName,
                category_type=category.CategoryType,
                description=category.Description,
                icon=category.Icon,
                color=category.Color,
                is_default=category.IsDefault,
                parent_category_id=category.ParentCategoryID if category.ParentCategoryID else None,
                is_active=category.IsActive,
                sort_order=category.SortOrder,
                created_at=category.CreatedAt
            ) if category else None,
            display_name=display_name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/user-categories/{user_category_id}", status_code=status.HTTP_200_OK)
async def delete_user_category(
    user_category_id: UUID = Path(..., description="ID của user category"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Xóa user category của user hiện tại"""
    # Kiểm tra xem user category có tồn tại và thuộc về user
    user_category = category_crud.get_user_category(
        db=db, 
        user_id=current_user.UserID, 
        user_category_id=user_category_id
    )
    if not user_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy user category hoặc không thuộc quyền sở hữu"
        )
    
    # Thực hiện xóa
    success = category_crud.delete_user_category(
        db=db, 
        user_id=current_user.UserID,
        user_category_id=user_category_id, 
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Không thể xóa user category"
        )
    
    return {"detail": "User category đã được xóa thành công"}


@router.get("/my-categories", response_model=CategoryDisplayListResponse)
async def get_my_category_display_names(
    category_type: Optional[str] = Query(None, description="Lọc theo loại danh mục (income/expense)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy tất cả tên hiển thị danh mục của user hiện tại"""
    if category_type:
        display_categories = category_crud.get_category_display_names_by_type(
            db=db, 
            user_id=current_user.UserID, 
            category_type=category_type
        )
    else:
        display_categories = category_crud.get_all_category_display_names(
            db=db, 
            user_id=current_user.UserID
        )
    
    return CategoryDisplayListResponse(
        display_categories=display_categories,
        total=len(display_categories)
    )

@router.get("/user-categories/", response_model=UserCategoryListResponse)
async def get_my_user_categories(
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng tối đa"),
    is_active: Optional[bool] = Query(None, description="Trạng thái hoạt động"),
    category_type: Optional[str] = Query(None, description="Loại danh mục"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách user categories của user hiện tại"""
    try:
        user_categories = category_crud.get_user_categories_by_user(
            db=db,
            user_id=current_user.UserID,
            skip=skip,
            limit=limit,
            is_active=is_active,
            category_type=category_type
        )
        
        total = category_crud.get_user_categories_count(
            db=db,
            user_id=current_user.UserID,
            is_active=is_active,
            category_type=category_type
        )
        
        # Chuyển đổi sang response format
        response_categories = []
        for result in user_categories:
            # ALWAYS extract as tuple since CRUD returns (UserCategory, Category)
            user_category, category = result
            
            # Handle the case where CategoryID might be accessed differently
            category_id = None
            if hasattr(user_category, 'CategoryID'):
                category_id = user_category.CategoryID
            elif hasattr(result, 'CategoryID'):
                category_id = result.CategoryID
            
            # If category_id exists but category is None, fetch it separately
            if category_id and not category:
                category = category_crud.get_category(db, category_id)
            
            # Get display name
            custom_name = None
            if hasattr(user_category, 'CustomName'):
                custom_name = user_category.CustomName
            elif hasattr(result, 'CustomName'):
                custom_name = result.CustomName
                
            display_name = custom_name
            if not display_name and category:
                display_name = category.CategoryName
            
            # Build the response
            response_categories.append(UserCategoryResponse(
                user_category_id=user_category.UserCategoryID,
                user_id=user_category.UserID,
                category_id=category_id if category_id else None,
                custom_name=custom_name,
                category_type=user_category.CategoryType,
                is_active=user_category.IsActive,
                created_at=user_category.CreatedAt,
                category=CategoryResponse(
                    category_id=category.CategoryID,
                    category_name=category.CategoryName,
                    category_type=category.CategoryType,
                    description=category.Description,
                    icon=category.Icon,
                    color=category.Color,
                    is_default=category.IsDefault,
                    parent_category_id=category.ParentCategoryID if category.ParentCategoryID else None,
                    is_active=category.IsActive,
                    sort_order=category.SortOrder,
                    created_at=category.CreatedAt
                ) if category else None,
                display_name=display_name or "Unknown Category"
            ))
        
        return UserCategoryListResponse(
            user_categories=response_categories,
            total=total
        )
        
    except Exception as e:
        print(f"Error in get_my_user_categories: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/user-categories/{user_category_id}", response_model=UserCategoryResponse)
async def update_user_category(
    user_category_id: UUID = Path(..., description="ID của user category"),
    user_category_update: UserCategoryUpdate = ...,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật user category"""
    # Kiểm tra quyền sở hữu
    existing_user_category = category_crud.get_user_category(db, user_category_id)
    if not existing_user_category or existing_user_category.UserID != current_user.UserID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user category"
        )
    
    updated_user_category = category_crud.update_user_category(
        db=db,
        user_category_id=user_category_id,
        updates=user_category_update
    )
    
    if not updated_user_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể cập nhật user category"
        )
    
    # Lấy thông tin category để trả về (nếu có)
    category = None
    if updated_user_category.CategoryID:
        category = category_crud.get_category(db, updated_user_category.CategoryID)
    
    display_name = updated_user_category.CustomName
    if not display_name and category:
        display_name = category.CategoryName
    
    return UserCategoryResponse(
        user_category_id=UUID(updated_user_category.UserCategoryID),
        user_id=UUID(updated_user_category.UserID),
        category_id=updated_user_category.CategoryID if updated_user_category.CategoryID else None,
        custom_name=updated_user_category.CustomName,
        category_type=updated_user_category.CategoryType,
        is_active=updated_user_category.IsActive,
        created_at=updated_user_category.CreatedAt,
        category=CategoryResponse(
            category_id=category.CategoryID,
            category_name=category.CategoryName,
            category_type=category.CategoryType,
            description=category.Description,
            icon=category.Icon,
            color=category.Color,
            is_default=category.IsDefault,
            parent_category_id=category.ParentCategoryID if category.ParentCategoryID else None,
            is_active=category.IsActive,
            sort_order=category.SortOrder,
            created_at=category.CreatedAt
        ) if category else None,
        display_name=display_name or "Unknown Category"
    )