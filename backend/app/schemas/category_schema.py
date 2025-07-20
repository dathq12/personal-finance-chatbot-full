# schemas/category_schema.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# Category Schemas
class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100, description="Tên danh mục")
    category_type: str = Field(..., min_length=1, max_length=20, description="Loại danh mục")
    description: Optional[str] = Field(None, max_length=500, description="Mô tả")
    icon: Optional[str] = Field(None, max_length=50, description="Icon")
    color: Optional[str] = Field(None, max_length=7, description="Màu sắc (hex)")
    is_default: bool = Field(False, description="Danh mục mặc định")
    sort_order: Optional[int] = Field(0, description="Thứ tự sắp xếp")

class CategoryCreate(CategoryBase):
    parent_category_id: Optional[UUID] = Field(None, description="ID danh mục cha")

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_type: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    parent_category_id: Optional[UUID] = None

class CategoryResponse(CategoryBase):
    category_id: UUID
    parent_category_id: Optional[UUID] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryWithChildren(CategoryResponse):
    children: List['CategoryResponse'] = []

# User Category Schemas
class UserCategoryBase(BaseModel):
    user_id: UUID = Field(..., description="ID người dùng")
    category_id: UUID = Field(..., description="ID danh mục")
    custom_name: Optional[str] = Field(None, max_length=100, description="Tên tùy chỉnh")

class UserCategoryCreate(UserCategoryBase):
    pass

class UserCategoryUpdate(BaseModel):
    custom_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserCategoryResponse(UserCategoryBase):
    user_category_id: UUID
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse] = None  # Thông tin danh mục
    
    class Config:
        from_attributes = True

# Response models for API
class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int
    page: int
    per_page: int

class UserCategoryListResponse(BaseModel):
    user_categories: List[UserCategoryResponse]
    total: int
    page: int
    per_page: int