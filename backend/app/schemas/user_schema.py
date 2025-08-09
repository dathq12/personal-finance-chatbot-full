# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    currency: Optional[str] = Field("VND", max_length=3)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

class UserResponse(UserBase):
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSessionBase(BaseModel):
    DeviceInfo: Optional[str] = None
    IPAddress: Optional[str] = None

class UserSessionCreate(UserSessionBase):
    UserID: UUID
    RefeshToken: str
    ExpiresAt: datetime

class UserSessionResponse(UserSessionBase):
    UserSessionID: UUID
    UserID: UUID
    ExpiresAt: datetime
    CreatedAt: datetime

    class Config:
        orm_mode = True