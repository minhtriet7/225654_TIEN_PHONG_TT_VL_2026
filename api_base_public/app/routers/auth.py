from fastapi import APIRouter, HTTPException, Form, Depends
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings
from app.models.base_db import UserDB
from app.security.security import get_current_user  # thêm dòng này

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 365

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    user_db = UserDB()
    existing = [u for u in user_db.get_all() if u["username"] == username]
    if existing:
        raise HTTPException(status_code=400, detail="Tên người dùng đã tồn tại!")

    hashed_pw = get_password_hash(password)
    user_db.add(username, hashed_pw, email)
    user_db.close()
    return {"message": "✅ Đăng ký thành công!"}


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user_db = UserDB()
    users = user_db.get_all()
    user_db.close()

    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu!")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu!")

    token = create_access_token({
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    })
    return {"access_token": token, "token_type": "bearer"}


# 🧩 API kiểm tra login
@router.get("/check")
def check_login(user=Depends(get_current_user)):
    return {
        "message": "✅ Token hợp lệ, người dùng đang đăng nhập!",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        },
    }
