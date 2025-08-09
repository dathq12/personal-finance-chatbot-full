# user_crud.py

from sqlalchemy.orm import Session
from app.models.user_model import User, UserSession, AuditLog
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse, UserSessionCreate
from app.auth.auth_dependency import get_current_user
from app.auth.password_hash import hash_password, verify_password

class UserCRUD:
    def get_user_by_id(self, db: Session, user_id: str) -> User:
        """Lấy thông tin người dùng theo ID"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> User:
        """Lấy thông tin người dùng theo email"""
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """Tạo người dùng mới"""
        hashed_password = hash_password(user_create.password)
        user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            phone=user_create.phone,
            currency=user_create.currency,
            password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def update_user(self, db: Session, user_id: str, user_update: UserUpdate) -> User:
        """Cập nhật thông tin người dùng"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        if user_update.email:
            user.email = user_update.email
        if user_update.full_name:
            user.full_name = user_update.full_name
        if user_update.phone:
            user.phone = user_update.phone
        if user_update.currency:
            user.currency = user_update.currency
        if user_update.is_active is not None:
            user.is_active = user_update.is_active
        
        db.commit()
        db.refresh(user)
        return user
    
    def update_user_password(self, db: Session, user_id: str, current_password: str, new_password: str) -> User:
        """Cập nhật mật khẩu người dùng"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user or not verify_password(current_password, user.password):
            return None
        
        user.password = hash_password(new_password)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: str) -> bool:
        """Xóa người dùng"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

class UserSessionCRUD:
    def create_user_session(self, db: Session, user_session_create: UserSessionCreate) -> UserSession:
        """Tạo phiên đăng nhập người dùng"""
        user_session = UserSession(
            user_id=user_session_create.user_id,
            refresh_token=user_session_create.refresh_token,
            expires_at=user_session_create.expires_at,
            device_info=user_session_create.device_info,
            ip_address=user_session_create.ip_address
        )
        db.add(user_session)
        db.commit()
        db.refresh(user_session)
        return user_session
    
    def get_user_sessions(self, db: Session, user_id: str) -> list[UserSession]:
        """Lấy danh sách phiên đăng nhập của người dùng"""
        return db.query(UserSession).filter(UserSession.user_id == user_id).all()