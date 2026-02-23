"""
Module Cơ sở dữ liệu (Database Module).
Đảm nhiệm (Single Responsibility): Quản lý kết nối SQLite và cung cấp các thao tác 
cơ bản dùng chung như tính toán token và sinh URL Gravatar.
"""

import sqlite3
import hashlib
from fastapi import HTTPException, status
from app.config import settings

class BaseDB:
    """
    Lớp trừu tượng quản lý kết nối và các thao tác cơ sở dữ liệu chung (SQLite).
    Được thiết kế theo chuẩn OOP, bao bọc logic kết nối an toàn bằng try/except.
    """
    def __init__(self):
        # Lấy tên file DB từ file .env thông qua file config.py
        self.db_path = getattr(settings, 'DB_NAME', 'database.sqlite')

    def get_connection(self):
        """Tạo và trả về đối tượng kết nối SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Row factory giúp trả về dữ liệu dạng dictionary thay vì tuple (dễ thao tác hơn)
            conn.row_factory = sqlite3.Row 
            return conn
        except sqlite3.Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi kết nối Cơ sở dữ liệu: {str(e)}"
            )

    @staticmethod
    def get_gravatar_url(email: str) -> str:
        """
        Tạo URL Gravatar từ email bằng thuật toán băm MD5.
        Lớp phòng thủ số 1 giúp tránh vỡ giao diện UI khi user chưa có Avatar.
        """
        if not email:
            return ""
        # Cắt khoảng trắng, chuyển thành chữ thường và băm MD5 theo đúng chuẩn Gravatar
        email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"

    def change_token_balance(self, user_id: int, amount: float, description: str, tx_type: str) -> bool:
        """
        Hệ thống tính phí Token (Billing Process).
        Cập nhật số dư của người dùng và ghi nhận log lịch sử giao dịch.
        """
        if tx_type not in ['in', 'out']:
            raise ValueError("Lỗi hệ thống: tx_type chỉ được nhận giá trị 'in' hoặc 'out'")

        # Tính toán giá trị âm dương dựa trên loại giao dịch
        delta = -float(amount) if tx_type == 'out' else float(amount)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Cập nhật số dư trực tiếp vào bảng users
                cursor.execute(
                    "UPDATE users SET token_balance = token_balance + ? WHERE id = ?",
                    (delta, user_id)
                )
                
                # 2. Ghi log vào bảng token_history để đối soát theo yêu cầu của thầy
                cursor.execute(
                    "INSERT INTO token_history (user_id, type, amount, description) VALUES (?, ?, ?, ?)",
                    (user_id, tx_type, float(amount), description)
                )
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Lỗi thao tác DB (change_token_balance): {e}")
            return False


class UserDB(BaseDB):
    """
    Class xử lý riêng cho bảng users.
    Kế thừa kết nối an toàn từ BaseDB.
    """
    def get_all(self):
        """Lấy danh sách tất cả người dùng."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                # Chuyển đổi sqlite3.Row thành dictionary để auth.py dễ xử lý
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Lỗi truy vấn: {e}")
            return []

    def add(self, username, hashed_password, email):
        """Thêm người dùng mới vào hệ thống."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Cấp mặc định 100 token cho user mới đăng ký để trải nghiệm
                cursor.execute(
                    "INSERT INTO users (username, password, email, token_balance) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, email, 100.0)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Lỗi thêm user: {e}")
            return False