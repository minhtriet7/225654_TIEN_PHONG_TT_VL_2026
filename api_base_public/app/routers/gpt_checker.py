"""
Module GPT Checker (Background Tasks).
Đảm nhiệm (Single Responsibility): Tiếp nhận văn bản, phân tích AI ngầm (không block server),
và cung cấp API Polling để Frontend hỏi vòng trạng thái.
Tuân thủ tuyệt đối cấu trúc TASK_WORKFLOW.md.
"""

import uuid
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from app.models.base_db import BaseDB

router = APIRouter(
    prefix="/api/v1/gpt-checker",
    tags=["GPT Checker AI"]
)

# Bộ nhớ tạm (In-Memory) lưu trạng thái các task đang chạy
# Thực tế đi làm có thể dùng Redis, nhưng ở đây dùng Dict cho tối ưu chi phí
task_results = {}

# --- SCHEMAS ---
class TextInput(BaseModel):
    text: str
    user_id: int

# --- CORE LOGIC ---
def background_prediction_task(task_id: str, text: str, user_id: int):
    """
    Hàm xử lý nền (Worker). 
    LƯU Ý: Dùng 'def' thường, không dùng 'async def' để FastAPI tự đẩy vào ThreadPool,
    đảm bảo Event Loop chính không bị nghẽn khi AI đang tính toán.
    """
    try:
        # 1. Giả lập thời gian model AI (VD: PhoBERT) chạy mất 5 giây
        time.sleep(5)
        
        # 2. Giả lập kết quả trả về từ mô hình AI
        ai_result = {
            "is_ai_generated": True,
            "confidence_score": 0.98,
            "details": "Phát hiện cấu trúc câu mang đặc trưng của LLM (GPT-4)."
        }
        
        # 3. Trừ tiền (Token) của người dùng thông qua BaseDB
        db = BaseDB()
        cost_token = 15.0  # Giả sử chi phí kiểm tra 1 lần là 15 token
        db.change_token_balance(
            user_id=user_id,
            amount=cost_token,
            description=f"Phi kiem tra GPT Checker (Task: {task_id[-6:]})",
            tx_type="out"
        )
        
        # 4. Cập nhật trạng thái thành 'done' để Frontend lấy dữ liệu
        task_results[task_id] = {
            "status": "done",
            "data": ai_result,
            "timestamp": time.time()
        }
        
    except Exception as e:
        # Bắt lỗi an toàn, tránh crash server
        task_results[task_id] = {
            "status": "failed",
            "error": str(e),
            "timestamp": time.time()
        }


# --- API ENDPOINTS ---

@router.post("/predict")
async def start_predict_gpt(input_data: TextInput, background_tasks: BackgroundTasks):
    """
    API Tiếp nhận văn bản. Trả về ngay task_id mà không bắt user phải chờ AI chạy xong.
    """
    # 1. Tạo UUID4 duy nhất cho tiến trình
    task_id = str(uuid.uuid4())
    
    # 2. Lưu trạng thái khởi tạo
    task_results[task_id] = {
        "status": "processing",
        "timestamp": time.time()
    }
    
    # 3. Đẩy tác vụ nặng vào hàng đợi Background Task
    background_tasks.add_task(
        background_prediction_task,
        task_id=task_id,
        text=input_data.text,
        user_id=input_data.user_id
    )
    
    return {"task_id": task_id, "message": "Hệ thống AI đang phân tích..."}

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    API Polling: Frontend sẽ gọi liên tục mỗi 2s để kiểm tra trạng thái Task.
    """
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task không tồn tại hoặc đã bị xóa khỏi bộ nhớ")
        
    return task_results[task_id]