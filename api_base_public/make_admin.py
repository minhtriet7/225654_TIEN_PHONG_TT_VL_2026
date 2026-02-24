import sqlite3

# Kết nối vào Database hiện tại
conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()

# 1. Tạo thêm cột phân quyền (nếu DB của bạn chưa có)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass # Nếu cột đã có sẵn thì bỏ qua lỗi này

# 2. Cấp quyền Admin cho tài khoản 'mt'
cursor.execute("UPDATE users SET role = 'admin', is_admin = 1 WHERE username = 'mt'")

conn.commit()
conn.close()

print("✅ THÀNH CÔNG! Tài khoản 'mt' đã được thăng cấp thành ADMIN!")