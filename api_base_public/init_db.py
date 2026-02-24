import sqlite3

# Kết nối tới file DB
conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()

# Tạo bảng users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    token_balance REAL DEFAULT 100.0
)
""")

# Tạo bảng token_history
cursor.execute("""
CREATE TABLE IF NOT EXISTS token_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()
print("✅ Đã khởi tạo cấu trúc Database thành công!")