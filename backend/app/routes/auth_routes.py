from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import UserRegister, UserLogin, ForgotPassword, ResetPassword, Token
from app.models import user_model
from app.utils.security import hash_password, verify_password, create_reset_token, verify_reset_token
from app.database import get_db
from app.auth.jwt_handler import create_access_token
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(user_model.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    new_user = user_model.User(
        FullName=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Đăng ký thành công"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    found = db.query(user_model.User).filter_by(email=user.email).first()
    if not found or not verify_password(user.password, found.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    access_token = create_access_token({"sub": found.email})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/forgot-password")
def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter_by(email=payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")
    
    reset_token = create_reset_token({"sub": user.email})
    # Giả lập gửi email bằng console log (hoặc dùng real email service)
    print(f"🔐 Reset token (giả lập gửi email): {reset_token}")
    return {"message": "Vui lòng kiểm tra email để đặt lại mật khẩu"}

@router.post("/reset-password")
def reset_password(payload: ResetPassword, db: Session = Depends(get_db)):
    data = verify_reset_token(payload.token)
    if not data:
        raise HTTPException(status_code=400, detail="Token không hợp lệ hoặc hết hạn")

    user = db.query(user_model.User).filter_by(email=data.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}

# phải có dòng này
__all__ = ["router"]