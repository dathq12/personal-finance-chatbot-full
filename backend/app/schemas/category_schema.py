# schemas/category_schema.py
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Literal

# Category Schemas
class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100, description="Tên danh mục")
    category_type: str = Field(..., min_length=1, max_length=50, description="Loại danh mục")
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

class CategoryResponse(BaseModel):
    category_name: str = Field(alias="CategoryName")
    category_type: str = Field(alias="CategoryType")
    category_id: UUID = Field(alias="CategoryID")
    parent_category_id: Optional[UUID] = Field(alias="ParentCategoryID", default=None)
    is_active: bool = Field(alias="IsActive")
    sort_order: int = Field(alias="SortOrder")
    created_at: datetime = Field(alias="CreatedAt")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# User Category Schemas
class UserCategoryBase(BaseModel):
    category_id: Optional[UUID] = Field(None, description="ID danh mục gốc (null nếu là category hoàn toàn tùy chỉnh)")
    custom_name: str = Field(..., min_length=1, max_length=100, description="Tên tùy chỉnh")

class UserCategoryCreate(UserCategoryBase):
    category_type: Literal["income", "expense"] = Field(..., description="Loại danh mục (income/expense)")  # Cần để phân loại

class UserCategoryUpdate(BaseModel):
    custom_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserCategoryResponse(UserCategoryBase):
    user_category_id: UUID
    user_id: UUID
    category_type: Literal["income", "expense"] = Field(..., description="Loại danh mục")
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse] = None  # Thông tin danh mục gốc (null nếu là custom)
    display_name: str = Field(..., description="Tên hiển thị")
    
    model_config = ConfigDict(from_attributes=True)

class CategoryDisplayResponse(BaseModel):
    """Schema cho danh sách display names của user"""
    display_name: str = Field(..., description="Tên hiển thị")
    category_type: Literal["income", "expense"] = Field(..., description="Loại danh mục")
    user_category_id: Optional[UUID] = Field(None, description="ID user category nếu có")
    category_id: Optional[UUID] = Field(None, description="ID danh mục gốc (null nếu là custom)")
    is_custom: bool = Field(..., description="Có phải là category hoàn toàn tùy chỉnh không")

    model_config = ConfigDict(from_attributes=True)
# Response models for API
class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)

class UserCategoryListResponse(BaseModel):
    user_categories: List[UserCategoryResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)
class CategoryDisplayListResponse(BaseModel):
    display_categories: List[CategoryDisplayResponse]
    total: int

    model_config = ConfigDict(from_attributes=True)