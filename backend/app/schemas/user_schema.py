# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


# -------------------- USERS --------------------
class UserBase(BaseModel):
    email: EmailStr = Field(..., alias="Email")
    full_name: str = Field(..., alias="FullName", min_length=1, max_length=255)
    phone: Optional[str] = Field(None, alias="Phone", max_length=20)
    currency: Optional[str] = Field("VND", alias="Currency", max_length=3)

    class Config:
        allow_population_by_field_name = True


class UserCreate(UserBase):
    password: str = Field(..., alias="PasswordHash", min_length=6, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, alias="Email")
    full_name: Optional[str] = Field(None, alias="FullName", min_length=1, max_length=255)
    phone: Optional[str] = Field(None, alias="Phone", max_length=20)
    currency: Optional[str] = Field(None, alias="Currency", max_length=3)
    is_active: Optional[bool] = Field(None, alias="IsActive")

    class Config:
        allow_population_by_field_name = True


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    user_id: UUID = Field(..., alias="UserID")
    is_active: bool = Field(..., alias="IsActive")
    created_at: datetime = Field(..., alias="CreatedAt")
    updated_at: datetime = Field(..., alias="UpdatedAt")
    last_login: Optional[datetime] = Field(None, alias="LastLogin")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., alias="Email")
    password: str = Field(..., alias="PasswordHash")

    class Config:
        allow_population_by_field_name = True


# -------------------- USER SESSIONS --------------------
class UserSessionBase(BaseModel):
    device_info: Optional[str] = Field(None, alias="DeviceInfo")
    ip_address: Optional[str] = Field(None, alias="IPAddress")

    class Config:
        allow_population_by_field_name = True


class UserSessionCreate(UserSessionBase):
    user_id: UUID = Field(..., alias="UserID")
    refresh_token: str = Field(..., alias="RefreshToken")
    expires_at: datetime = Field(..., alias="ExpiresAt")


class UserSessionResponse(UserSessionBase):
    session_id: UUID = Field(..., alias="SessionID")
    user_id: UUID = Field(..., alias="UserID")
    refresh_token: str = Field(..., alias="RefreshToken")
    expires_at: datetime = Field(..., alias="ExpiresAt")
    created_at: datetime = Field(..., alias="CreatedAt")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
