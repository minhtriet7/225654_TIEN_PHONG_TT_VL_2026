"""
Module Chatbot API (Router).
Đảm nhiệm (Single Responsibility): Tiếp nhận câu hỏi, điều phối qua LangGraph (AI Engine),
đếm số lượng token sử dụng, trừ tiền người dùng và trả kết quả về Frontend.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.base_db import BaseDB
from app.security.security import get_current_user

# Thư viện đếm token của OpenAI theo chuẩn yêu cầu
import tiktoken 

router = APIRouter(
    prefix="/api/v1/chatbot",
    tags=["AI Chatbot Engine"]
)

# --- SCHEMAS ---
class ChatRequest(BaseModel):
    question: str

# --- UTILS ---
def count_tokens(text: str, model="gpt-4o-mini") -> int:
    """Đếm chính xác số lượng token của chuỗi văn bản bằng tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback nếu model không nhận diện được
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

# --- API ENDPOINTS ---
@router.post("/ask")
async def ask_chatbot(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    API Xử lý Chat chính (Tích hợp RAG & Billing).
    Bắt buộc User phải đăng nhập (có token JWT) mới được chat.
    """
    user_id = current_user.get("id")
    
    # 1. Gọi lõi xử lý LangGraph (Mock logic để mô phỏng luồng RAG)
    # Trong thực tế, bạn sẽ gọi: generate_node(retrieve_node(request.question))
    simulated_answer = f"Nam mô A Di Đà Phật, đây là câu trả lời được AI sinh ra cho câu hỏi: '{request.question}'"
    simulated_sources = ["nguon_goc_phat_phap.pdf", "lich_su_chua.txt"]
    
    # 2. Đếm Token đầu vào (câu hỏi) + đầu ra (câu trả lời)
    total_text = request.question + simulated_answer
    used_tokens = count_tokens(total_text)
    
    # Tính phí: Giả sử 1 token = 0.5 điểm phí
    tokens_charged = float(used_tokens * 0.5)
    
    # 3. Trừ tiền trong Database
    db = BaseDB()
    success = db.change_token_balance(
        user_id=user_id,
        amount=tokens_charged,
        description="Phi su dung Chatbot LangGraph RAG",
        tx_type="out"
    )
    
    if not success:
        raise HTTPException(
            status_code=402, 
            detail="Thanh toán thất bại: Tài khoản không đủ số dư token."
        )
        
    # Lấy số dư mới nhất (Mock data giả lập, thực tế sẽ lấy hàm get_balance từ DB)
    current_balance = 849.5 
    
    # 4. Trả về ĐÚNG cấu trúc JSON mà Frontend App.tsx yêu cầu
    return {
        "answer": simulated_answer,
        "tokens_charged": tokens_charged,
        "user_token_balance": current_balance,
        "sources": simulated_sources
    }