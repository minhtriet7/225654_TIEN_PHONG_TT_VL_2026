"""
Module Bảo mật (Security Module).
Đảm nhiệm (Single Responsibility): Mã hóa mật khẩu, tạo token JWT, xác thực người dùng 
và kiểm tra API Key bảo vệ hệ thống.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# --- 1. CẤU HÌNH BẢO MẬT MẬT KHẨU & JWT ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/1.0.0/auth/login")

class SecurityHelper:
    """
    Class chứa các phương thức tiện ích về bảo mật.
    Tuân thủ OOP và không chứa hard-code.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Kiểm tra mật khẩu người dùng nhập có khớp với mật khẩu đã băm trong DB hay không."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Băm mật khẩu trước khi lưu vào Database."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Tạo JWT Access Token dựa trên Payload."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm="HS256"
        )
        return encoded_jwt

# --- 2. DEPENDENCIES DÀNH CHO USER (JWT) ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Giải mã JWT Token để lấy thông tin người dùng."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin (Token không hợp lệ)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
            
        token_data = {
            "id": payload.get("id"),
            "email": email,
            "is_admin": payload.get("is_admin", False)
        }
        return token_data
        
    except JWTError:
        raise credentials_exception

def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Dependency Phân quyền (RBAC): Chỉ cho phép Admin truy cập."""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền truy cập chức năng này (Admin Access Required)"
        )
    return current_user


# --- 3. DEPENDENCIES DÀNH CHO HỆ THỐNG (API KEY) ---
# Khai báo tên Header chứa API Key (Thường dùng X-API-Key)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency kiểm tra API Key để bảo vệ các Endpoint hệ thống (như file_upload).
    Khớp với biến API_KEY trong file .env và config.py
    """
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Từ chối truy cập: API Key không hợp lệ hoặc bị thiếu trong Header"
    )