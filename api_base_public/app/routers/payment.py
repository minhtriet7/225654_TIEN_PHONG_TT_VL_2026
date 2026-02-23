"""
Module Thanh toán (Payment Router).
Đảm nhiệm (Single Responsibility): Quản lý luồng nạp tiền tự động, tạo mã QR,
bảo mật ID hóa đơn (XOR) và cơ chế Polling đối soát giao dịch ngân hàng (SePay).
"""

import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings

# Khởi tạo Router cho Payment
router = APIRouter(
    prefix="/api/v1/payment",
    tags=["Thanh Toán"]
)

# --- THUẬT TOÁN BẢO MẬT ID (XOR Obfuscation) ---
# Dùng để giấu ID thật của hóa đơn trong Database, tránh việc user đoán được ID
SECRET_XOR_KEY = 0x5EAFB 

def encode_payment_id(p_id: int) -> str:
    """Mã hóa ID số nguyên thành chuỗi HEX."""
    return hex(p_id ^ SECRET_XOR_KEY)[2:].upper()

def decode_payment_id(hex_str: str) -> int:
    """Giải mã chuỗi HEX trở lại thành ID số nguyên."""
    try:
        return int(hex_str, 16) ^ SECRET_XOR_KEY
    except ValueError:
        raise HTTPException(status_code=400, detail="Mã giao dịch không hợp lệ")


# --- SCHEMAS (Pydantic) ---
class PaymentCreateRequest(BaseModel):
    package_id: int
    amount_vnd: float


# --- API ENDPOINTS ---

@router.post("/create")
async def create_payment(req: PaymentCreateRequest):
    """
    API Tạo hóa đơn nạp tiền.
    Thực tế: Hàm này sẽ lưu record vào DB với status 'pending' và trả về mã HEX.
    """
    # Demo logic: Giả sử sau khi insert vào DB, ta có ID hóa đơn là 105
    mock_inserted_id = 105 
    hex_id = encode_payment_id(mock_inserted_id)
    
    # Mã nội dung chuyển khoản: VD: "DEMOAPINAPTOKEN3E5"
    transfer_content = f"{settings.TITLE_APP}NAPTOKEN{hex_id}".replace(" ", "").upper()
    
    return {
        "status": "success",
        "payment_id": mock_inserted_id,
        "hex_id": hex_id,
        "transfer_content": transfer_content,
        "message": "Vui lòng chuyển khoản với đúng nội dung trên."
    }

@router.get("/status/{payment_id}")
async def check_payment_status(payment_id: int):
    """
    API Polling (Hỏi vòng).
    Frontend sẽ gọi API này mỗi 5 giây để kiểm tra xem tiền đã vào tài khoản chưa.
    """
    # 1. Lấy thông tin hóa đơn từ DB (Giả lập)
    payment_record = {
        "id": payment_id,
        "amount_vnd": 50000,
        "status": "pending"
    }
    
    if payment_record["status"] == "completed":
        return {"status": "completed", "message": "Thanh toán đã hoàn tất."}

    # 2. Xử lý so khớp với lịch sử SePay (Reconciliation Logic)
    target_hex = encode_payment_id(payment_id)
    prefix = settings.TITLE_APP.replace(" ", "").upper() + "NAPTOKEN"
    pattern = rf"{prefix}([A-Fa-f0-9]+)"
    
    # Mock data mô phỏng kết quả trả về từ SePay API (ngân hàng)
    mock_sepay_history = [
        {"id": 1, "amount_in": 50000, "content": f"Nguyen Van A chuyen {prefix}{target_hex}"},
        {"id": 2, "amount_in": 20000, "content": "Tien an trua"}
    ]
    
    is_matched = False
    for tx in mock_sepay_history:
        content = tx.get('content', '')
        amount = float(tx.get('amount_in', 0))
        
        # Dùng Regex tìm mã nạp trong nội dung tin nhắn lộn xộn
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            found_hex = match.group(1).upper()
            if found_hex == target_hex and amount >= payment_record['amount_vnd']:
                is_matched = True
                break # Trùng khớp! Dừng quét.

    if is_matched:
        # Thực tế: Tại đây bạn sẽ gọi db.change_token_balance(...) để cộng tiền cho user
        # và UPDATE status của payment_record thành 'completed'.
        return {"status": "completed", "message": "Nạp tiền thành công!"}
    else:
        return {"status": "pending", "message": "Đang chờ thanh toán..."}