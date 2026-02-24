"""
Module Chatbot AI (Tích hợp 3 mô hình AI thật).
Đảm nhiệm: Nhận câu hỏi, gọi đồng thời 3 LLM (MoE), đếm token và trừ tiền vào Database.
"""
import asyncio
import tiktoken
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from groq import AsyncGroq
from openai import AsyncOpenAI
from google import genai

from app.config import settings
from app.security.security import get_current_user
from app.models.base_db import BaseDB 

# Khởi tạo router
router = APIRouter(prefix="/api/v1/chatbot", tags=["AI Chatbot Engine"])

# --- 1. SCHEMAS ĐẦU VÀO ---
class ChatRequest(BaseModel):
    question: str

# --- 2. HÀM ĐẾM TOKEN CHUẨN ---
def count_tokens(text: str) -> int:
    """Đếm số lượng token chính xác bằng thư viện tiktoken của OpenAI."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())

# --- 3. SERVICE GỌI AI ĐA MÔ HÌNH (MoE) ---
class AIEngineService:
    def __init__(self):
        # Đọc Key từ file config.py (đã lấy từ .env)
        self.groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.or_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1", 
            api_key=settings.OPENROUTER_API_KEY
        )
        self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def _ask_groq(self, question: str) -> str:
        try:
            res = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": question}]
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"Lỗi Groq: {e}"

    async def _ask_openrouter(self, question: str) -> str:
        try:
            res = await self.or_client.chat.completions.create(
                model="qwen/qwen-2.5-72b-instruct",
                messages=[{"role": "user", "content": question}]
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"Lỗi OpenRouter: {e}"

    async def _ask_gemini(self, question: str) -> str:
        try:
            # Gemini SDK chạy trong threadpool để không block server
            res = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model='gemini-2.5-flash',
                contents=question
            )
            return res.text.strip()
        except Exception as e:
            return f"Lỗi Gemini: {e}"

    async def get_final_answer(self, question: str) -> str:
        """Hàm điều phối: Chạy 3 AI cùng lúc và dùng Groq tổng hợp lại."""
        # Chạy song song để tiết kiệm thời gian
        ans_groq, ans_or, ans_gemini = await asyncio.gather(
            self._ask_groq(question),
            self._ask_openrouter(question),
            self._ask_gemini(question)
        )

        prompt_tong_hop = f"""
        Bạn là một AI chuyên gia tổng hợp thông tin. Hãy đọc 3 ý kiến dưới đây cho câu hỏi: "{question}"
        1 (Groq): {ans_groq}
        2 (OpenRouter): {ans_or}
        3 (Gemini): {ans_gemini}
        Dựa vào 3 ý kiến trên, hãy đưa ra MỘT câu trả lời cuối cùng chính xác và chuyên nghiệp nhất (ngắn gọn, trực diện).
        """
        return await self._ask_groq(prompt_tong_hop)

# --- 4. API ENDPOINT CHÍNH ---
@router.post("/ask")
async def ask_chatbot(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    
    # 1. Gọi hệ thống AI Đa Mô Hình
    ai_service = AIEngineService()
    real_answer = await ai_service.get_final_answer(request.question)
    
    # 2. Đếm Token đầu vào + đầu ra
    used_tokens = count_tokens(request.question + real_answer)
    
    # Tính phí: 1 token = 0.5 điểm
    tokens_charged = float(used_tokens * 0.5)
    
    # 3. Trừ tiền trực tiếp trong Database
    db = BaseDB()
    success = db.change_token_balance(
        user_id=user_id,
        amount=tokens_charged,
        description="Phí sử dụng Chatbot Multi-Model",
        tx_type="out"
    )
    
    if not success:
        raise HTTPException(
            status_code=402, 
            detail="Tài khoản không đủ số dư Token để thực hiện tác vụ này."
        )
        
    return {
        "answer": real_answer,
        "tokens_charged": tokens_charged,
        "user_token_balance": "Đã trừ thành công (Xem trong DB)",
        "sources": ["Groq 70B", "Qwen 72B", "Gemini Flash"]
    }