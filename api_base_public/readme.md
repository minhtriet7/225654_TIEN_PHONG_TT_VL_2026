# FastAPI Base Public API - AI Chatbot & Fintech Tích hợp

Dự án này được phát triển dựa trên bản mẫu (template) cơ bản của môn học, được mở rộng và tích hợp thêm các tính năng nâng cao như AI Chatbot Đa mô hình, Hệ thống thanh toán (Billing), Xử lý Hàng đợi bất đồng bộ (Async Task) và Phân quyền Quản trị (RBAC).

**Sinh viên thực hiện:** Huỳnh Nguyễn Minh Triết (MSSV: 225654)
**Framework:** FastAPI (Python)

---

## ✨ Tính năng chính (Core Features)

- **Xác thực và Phân quyền (Auth & RBAC):** Hỗ trợ đăng ký, đăng nhập bảo mật bằng JWT (JSON Web Token) cùng với xác thực qua API Key. Phân quyền Role-Based Access Control (chặn truy cập API Admin đối với User thường - Lỗi 403).
- **AI Chatbot & Billing:** Tích hợp các mô hình LLM (Groq, Qwen, Gemini). Tự động tính toán số token tiêu thụ và trừ tiền trực tiếp vào ví người dùng trong cơ sở dữ liệu.
- **Xử lý Bất đồng bộ (Async Task Queue):** Áp dụng cho tính năng phân tích văn bản dài (GPT Checker) giúp không gây nghẽn Server (trả về `task_id` và hỗ trợ Polling tra cứu kết quả).
- **Fintech Payment:** Tạo lệnh nạp tiền, sinh mã giao dịch bảo mật (HEX ID) và đối soát trạng thái đơn hàng.
- **Quản lý File:** API upload, download và xem trực tiếp (preview) các tệp tin. Tự động mã hóa tên file bằng UUID để chống ghi đè dữ liệu.
- **Cơ sở dữ liệu:** Tích hợp SQLite gọn nhẹ, dễ dàng triển khai.

## 🚀 Công nghệ sử dụng

- Python 3.x
- FastAPI & Uvicorn (ASGI Server)
- SQLite (Cơ sở dữ liệu)
- Pydantic (Data validation)
- Python-JOSE (JWT) & Passlib (Bcrypt Hashing)

## 📂 Cấu trúc thư mục

```text
api_base_public/
├── app/
│   ├── models/          # Định nghĩa các mô hình dữ liệu (Database & Pydantic)
│   ├── routers/         # Định nghĩa các endpoint API (auth, file_upload, chatbot...)
│   ├── security/        # Xử lý xác thực (JWT, API Key, RBAC Dependency)
│   ├── utils/           # Các công cụ tiện ích
│   ├── config.py        # Cấu hình ứng dụng từ .env
│   └── main.py          # Điểm khởi đầu của ứng dụng
├── utils/
│   └── download/        # Nơi lưu file upload có mã hóa UUID
├── init_db.py           # Script tự động khởi tạo cơ sở dữ liệu và bảng
├── .env.example         # File mẫu cấu hình biến môi trường
├── requirements.txt     # Danh sách thư viện phụ thuộc
└── readme.md            # Tài liệu hướng dẫn dự án


# FastAPI Base Public API

Dự án này là một bản mẫu (template) cơ bản cho việc xây dựng API sử dụng FastAPI, tích hợp sẵn các tính năng quan trọng như xác thực người dùng (JWT), quản lý file và kết nối cơ sở dữ liệu MySQL.

## ✨ Tính năng chính

- **Xác thực và phân quyền (Auth):** Hỗ trợ đăng ký, đăng nhập và bảo mật bằng JWT (JSON Web Token) cùng với xác thực qua API Key.
- **Quản lý File:** API upload, download và xem trực tiếp (preview) các tệp tin (hình ảnh, video, audio).
- **Cơ sở dữ liệu:** Tích hợp SQLAlchemy và kết nối MySQL.
- **Cấu trúc Modular:** Phân chia thư mục rõ ràng (routers, models, security, utils) giúp dễ dàng mở rộng.
- **Tài liệu tự động:** Tích hợp sẵn Swagger UI và ReDoc.
- **CORS:** Cấu hình sẵn Middleware xử lý Cross-Origin Resource Sharing.

## 🚀 Công nghệ sử dụng

- Python 3.x
- FastAPI
- Uvicorn (ASGI Server)
- MySQL Connector
- Pydantic (Data validation)
- Python-JOSE (JWT)
- SQLAlchemy

## 📋 Yêu cầu hệ thống

- Đã cài đặt Python (phiên bản 3.8 trở lên).
- Cơ sở dữ liệu MySQL đang hoạt động.

## 🛠️ Hướng dẫn cài đặt

1. **Clone repository:**
   ```bash
   git clone <repository_url>
   cd api_base_public
   ```

2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình biến môi trường:**
   Tạo file `.env` tại thư mục gốc và cấu hình các thông số sau:
   ```env
   API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ALLOW_ORIGINS=["*"]
   TITLE_APP=FastAPI_Base_API
   VERSION_APP=v1

   # Database settings
   HOST=localhost
   USER=root
   PASSWORD=your_password
   DATABASE=your_database_name
   ```

## 🏃 Cách chạy dự án

Bạn có thể chạy dự án bằng script `run_api.py`:

```bash
python run_api.py
```

Hoặc sử dụng lệnh uvicorn trực tiếp:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 60074 --reload
```

Sau khi chạy, bạn có thể truy cập tài liệu API tại:
- Swagger UI: `http://localhost:60074/api/v1/docs`
- ReDoc: `http://localhost:60074/api/v1/redoc`

## 📂 Cấu trúc thư mục

```text
api_base_public/
├── app/
│   ├── models/          # Định nghĩa các mô hình dữ liệu (Database & Pydantic)
│   ├── routers/         # Định nghĩa các endpoint API
│   ├── security/        # Xử lý xác thực (JWT, API Key)
│   ├── utils/           # Các công cụ tiện ích (Download, file handling)
│   ├── config.py        # Cấu hình ứng dụng từ .env
│   └── main.py          # Điểm khởi đầu của ứng dụng
├── .env                 # File cấu hình môi trường (không commit lên git)
├── requirements.txt     # Danh sách thư viện phụ thuộc
├── run_api.py           # Script chạy ứng dụng
└── start.sh             # Script khởi động trên Linux
```

## 🛠️ Danh sách API chính

### 🔐 Authentication
- `POST /api/v1/auth/register`: Đăng ký tài khoản mới.
- `POST /api/v1/auth/login`: Đăng nhập lấy token.
- `GET /api/v1/auth/check`: Kiểm tra trạng thái đăng nhập.

### 📁 File Upload
- `POST /api/v1/upload-file/upload/`: Tải tệp lên hệ thống.
- `GET /api/v1/upload-file/download/{filename}`: Tải tệp về máy.
- `GET /api/v1/upload-file/view/{filename}`: Xem trước tệp (hình ảnh, video...).

### ⚙️ Base API
- `POST /api/v1/base/base-url/`: API mẫu sử dụng xác thực JWT.
- `POST /api/v1/base/base-api/`: API mẫu sử dụng xác thực API Key.

## 📄 Giấy phép

Dự án này được phát hành dưới giấy phép MIT.
