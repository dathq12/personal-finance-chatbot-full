# routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.user_service import UserService
from app.models.user_model import User, UserSession  # nếu có
from sqlalchemy import and_
from datetime import datetime
from app.schemas.user_schema import (
    UserCreate, UserOut, UserUpdate, UserUpdatePassword,
    UserLogin, Token, TokenRefresh, UserSessionOut
)
from app.auth.auth_dependency import get_current_user, get_current_admin_user

router = APIRouter(prefix="/users", tags=["users"])

# Dependency to get current user is now imported from auth.dependencies

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    return UserService.create_user(db, user)

@router.post("/login", response_model=Token)
def login_user(user_login: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user"""
    # Authenticate user
    user = UserService.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    UserService.update_last_login(db, user.UserID)
    
    # Create session
    device_info = request.headers.get("user-agent")
    ip_address = request.client.host
    session = UserService.create_user_session(db, user.UserID, device_info, ip_address)
    
    # Generate access token
    access_token = UserService.create_access_token(user.UserID)
    
    return {
        "access_token": access_token,
        "refresh_token": session.RefreshToken,
        "token_type": "bearer",
        "expires_in": 3600  # 1 hour
    }

@router.post("/refresh", response_model=Token)
def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token"""
    # Find session with refresh token
    session = db.query(UserSession).filter(
        and_(
            UserSession.RefreshToken == token_refresh.refresh_token,
            UserSession.ExpiresAt > datetime.utcnow()
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if user is still active
    user = UserService.get_user_by_id(db, session.UserID)
    if not user or not user.IsActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )
    
    # Generate new access token
    access_token = UserService.create_access_token(user.UserID)
    
    return {
        "access_token": access_token,
        "refresh_token": session.RefreshToken,  # Keep same refresh token
        "token_type": "bearer",
        "expires_in": 3600
    }

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserOut)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    return UserService.update_user(db, current_user.UserID, user_update)

@router.put("/me/password")
def update_current_user_password(
    password_update: UserUpdatePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user password"""
    UserService.update_password(db, current_user.UserID, password_update)
    return {"message": "Password updated successfully"}

@router.get("/me/sessions", response_model=List[UserSessionOut])
def get_current_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's active sessions"""
    return UserService.get_user_sessions(db, current_user.UserID)

@router.delete("/me/sessions/{session_id}")
def revoke_user_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke specific user session"""
    success = UserService.revoke_user_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session revoked successfully"}

@router.delete("/me/sessions")
def revoke_all_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all user sessions"""
    UserService.revoke_all_user_sessions(db, current_user.UserID)
    return {"message": "All sessions revoked successfully"}

@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user (revoke all sessions)"""
    UserService.revoke_all_user_sessions(db, current_user.UserID)
    return {"message": "Logged out successfully"}

# Admin endpoints (require admin role)
@router.get("/", response_model=List[UserOut])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get list of users (admin only)"""
    return UserService.get_users(db, skip=skip, limit=limit, search=search)

@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Get user by ID (admin only)"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user_by_id(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Update user by ID (admin only)"""
    return UserService.update_user(db, user_id, user_update)

@router.put("/{user_id}/activate", response_model=UserOut)
def activate_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Activate user account (admin only)"""
    return UserService.activate_user(db, user_id)

@router.put("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Deactivate user account (admin only)"""
    return UserService.deactivate_user(db, user_id)

@router.put("/{user_id}/verify-email", response_model=UserOut)
def verify_user_email(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Verify user email (admin only)"""
    return UserService.verify_email(db, user_id)

@router.delete("/{user_id}")
def delete_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin only
):
    """Delete user account (admin only)"""
    UserService.delete_user(db, user_id)
    return {"message": "User deleted successfully"}