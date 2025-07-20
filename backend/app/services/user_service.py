# user_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from passlib.context import CryptContext
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta
import secrets

from app.models.user_model import User, UserSession
from app.schemas.user_schema import UserCreate, UserUpdate, UserUpdatePassword

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.UserID == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.Email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
        """Get list of users with pagination and optional search"""
        query = db.query(User)
        
        if search:
            search_filter = or_(
                User.FullName.contains(search),
                User.Email.contains(search),
                User.Phone.contains(search)
            )
            query = query.filter(search_filter)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create new user"""
        # Check if email already exists
        existing_user = UserService.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = UserService.hash_password(user.password)
        
        # Create user object
        db_user = User(
            Email=user.email,
            PasswordHash=hashed_password,
            FullName=user.full_name,
            Phone=user.phone,
            AvatarURL=user.avatar_url,
            TimeZone=user.time_zone,
            Currency=user.currency
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> User:
        """Update user information"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_user, field.title().replace('_', '')):
                setattr(db_user, field.title().replace('_', ''), value)
        
        # Update timestamp
        db_user.UpdatedAt = datetime.utcnow()
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_password(db: Session, user_id: UUID, password_update: UserUpdatePassword) -> bool:
        """Update user password"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not UserService.verify_password(password_update.current_password, db_user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = UserService.hash_password(password_update.new_password)
        db_user.PasswordHash = new_hashed_password
        db_user.UpdatedAt = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    def activate_user(db: Session, user_id: UUID) -> User:
        """Activate user account"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.IsActive = True
        db_user.UpdatedAt = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: UUID) -> User:
        """Deactivate user account"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.IsActive = False
        db_user.UpdatedAt = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def verify_email(db: Session, user_id: UUID) -> User:
        """Verify user email"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db_user.EmailVerified = True
        db_user.UpdatedAt = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Delete user (soft delete by deactivating)"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete by deactivating
        db_user.IsActive = False
        db_user.UpdatedAt = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not UserService.verify_password(password, user.PasswordHash):
            return None
        if not user.IsActive:
            return None
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.LastLogin = datetime.utcnow()
            db.commit()

    @staticmethod
    def create_user_session(db: Session, user_id: UUID, device_info: str = None, ip_address: str = None) -> UserSession:
        """Create new user session"""
        # Generate refresh token
        refresh_token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
        
        session = UserSession(
            UserID=user_id,
            RefreshToken=refresh_token,
            DeviceInfo=device_info,
            IPAddress=ip_address,
            ExpiresAt=expires_at
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: UUID) -> List[UserSession]:
        """Get all active sessions for user"""
        return db.query(UserSession).filter(
            and_(
                UserSession.UserID == user_id,
                UserSession.ExpiresAt > datetime.utcnow()
            )
        ).all()
    
    @staticmethod
    def revoke_user_session(db: Session, session_id: UUID) -> bool:
        """Revoke specific user session"""
        session = db.query(UserSession).filter(UserSession.SessionID == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: UUID) -> bool:
        """Revoke all sessions for user"""
        db.query(UserSession).filter(UserSession.UserID == user_id).delete()
        db.commit()
        return True