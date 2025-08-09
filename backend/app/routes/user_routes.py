# routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.user_model import User, UserSession  # nếu có
from datetime import datetime
from app.schemas.user_schema import (
    UserCreate, UserResponse, UserUpdate, UserUpdatePassword,
    UserLogin, Token, TokenRefresh, UserSessionOut
)
from app.auth.auth_dependency import get_current_user, get_current_admin_user
from app.crud.user_crud import UserCRUD

router = APIRouter(prefix="/users", tags=["users"])

# Dependency to get current user is now imported from auth.dependencies

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    #check ìf user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    """Register a new user"""
    db_user = UserCRUD.UserCreate(db = db, user = user)
    return db_user

@router.post("/login", response_model=Token)
def login_user(user_login: UserLogin, request: Request, db: Session = Depends(get_db)):
    # check if user exists and password is correct
    if not user_login.email or not user_login.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
