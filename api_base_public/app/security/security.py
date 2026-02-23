"""
Module Bảo mật (Security Module).
Đảm nhiệm (Single Responsibility): Mã hóa mật khẩu, tạo token JWT và xác thực người dùng.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Cấu hình CryptContext để mã hóa mật khẩu (sử dụng thuật toán bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Khai báo schema OAuth2 để lấy token từ Header (Bearer Token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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
        """
        Tạo JWT Access Token dựa trên Payload.
        Thời gian hết hạn mặc định nếu không truyền vào là 30 phút.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        
        # Tạo token bằng chuỗi SECRET_KEY lấy từ biến môi trường
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm="HS256"
        )
        return encoded_jwt

# Hàm Dependency dùng để gắn vào các API cần bảo vệ
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Giải mã JWT Token để lấy thông tin người dùng.
    Có xử lý lỗi (Exception Handling) đẩy về mã 401 nếu token sai hoặc hết hạn.
    """
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
            
        # Lưu ý: Theo file SECURITY_GUIDE.md, ở bước này bạn cần gọi DB 
        # để kiểm tra lại user có tồn tại không. 
        # Chúng ta sẽ trả về dict tạm thời, khi làm xong DB sẽ nối vào sau.
        token_data = {
            "id": payload.get("id"),
            "email": email,
            "is_admin": payload.get("is_admin", False)
        }
        return token_data
        
    except JWTError:
        raise credentials_exception

def get_current_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency Phân quyền (RBAC): Chỉ cho phép Admin truy cập.
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền truy cập chức năng này (Admin Access Required)"
        )
    return current_user