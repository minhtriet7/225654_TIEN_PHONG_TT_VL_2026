"""
Module Quản trị (Admin Router).
Đảm nhiệm: Các chức năng dành riêng cho Admin (có phân quyền), 
bao gồm tính năng Đồng bộ SEO vật lý (Dynamic HTML Modification).
"""

import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.security.security import get_current_admin

# Tạo router với prefix /admin
router = APIRouter(prefix="/admin", tags=["admin"])

# --- SCHEMAS ---
class SEOData(BaseModel):
    site_title: str
    description: str
    keywords: str
    author: str
    favicon_url: str
    logo_url: str

# --- API ENDPOINTS ---
@router.post("/seo/update")
def update_index_html_seo(data: SEOData, admin_user: dict = Depends(get_current_admin)):
    """
    API cập nhật meta tags trực tiếp vào file index.html của Frontend.
    Chỉ chạy được khi request có chứa Token JWT của tài khoản có quyền Admin.
    """
    # Đường dẫn vật lý tới file HTML (giả định nằm ở thư mục frontend ngang hàng với api_base_public)
    path = "../frontend/index.html" 
    
    try:
        # 1. Đọc nội dung file hiện tại
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 2. Phẫu thuật thay thế bằng Regex
        # Thay Title
        content = re.sub(r'<title>.*?</title>', f'<title>{data.site_title}</title>', content)

        # Danh sách Meta tags cần thay đổi
        meta_maps = {
            "description": data.description,
            "keywords": data.keywords,
            "author": data.author,
            "og:title": data.site_title,
            "og:description": data.description
        }

        # Vòng lặp thay thế từng Meta tag
        for key, value in meta_maps.items():
            pattern = fr'<(meta\s+[^>]*?(?:name|property)=["\']{re.escape(key)}["\'][^>]*?content=)["\'].*?["\']([^>]*?)>'
            replacement = fr'<\1"{value}"\2>'
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # Thay Favicon
        content = re.sub(r'<link\s+rel=["\']icon["\'][^>]*?href=["\'].*?["\']', f'<link rel="icon" href="{data.favicon_url}"', content)

        # 3. Ghi đè lại file
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return {"message": "✅ Cập nhật SEO vào file index.html thành công!"}
        
    except FileNotFoundError:
        # Trả về lỗi thân thiện nếu chưa có thư mục frontend
        return {"message": "⚠️ Lỗi: Không tìm thấy file frontend/index.html (Có thể bạn chưa tạo phần Frontend)"}