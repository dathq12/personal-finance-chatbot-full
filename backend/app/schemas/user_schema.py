# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    time_zone: Optional[str] = Field("SE Asia Standard Time", max_length=50)
    currency: Optional[str] = Field("VND", max_length=3)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    time_zone: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)

class UserOut(UserBase):
    user_id: UUID
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str

class UserSessionOut(BaseModel):
    session_id: UUID
    device_info: Optional[str]
    ip_address: Optional[str]
    expires_at: datetime
    created_at: datetime
    
    class Config:
        orm_mode = True