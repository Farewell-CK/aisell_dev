from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from utils.opening_generator import OpeningGenerator, generate_opening
import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "opening_service.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="开场白生成服务", description="自动生成个性化聊天开场白")

# 请求模型
class CustomerInfo(BaseModel):
    name: str
    company: str
    position: Optional[str] = ""
    industry: Optional[str] = ""
    city: Optional[str] = ""

class SalesInfo(BaseModel):
    name: str
    company: str
    product: str
    advantage: Optional[str] = ""
    scenarios: Optional[str] = ""

class ReferrerInfo(BaseModel):
    name: str
    relationship: Optional[str] = "朋友"

class PersonalizedOpeningRequest(BaseModel):
    tenant_id: int
    wechat_id: int
    task_id: str
# 响应模型
class OpeningResponse(BaseModel):
    tenant_id: int
    task_id: int
    session_id: str
    status: str
    # opening: Optional[str] = None


@app.get("/")
async def root():
    """服务根路径"""
    return {
        "message": "开场白生成服务",
        "version": "1.0.0",
        "endpoints": [
            "/generate/personalized",
        ]
    }

@app.post("/generate/personalized", response_model=OpeningResponse)
async def generate_personalized_opening(request: PersonalizedOpeningRequest):
    """生成个性化开场白"""
    try:
        tenant_id = request.tenant_id
        task_id = request.task_id
        wechat_id = request.wechat_id
        # session_id = request.session_id
        generator = OpeningGenerator()
        result = await generator.generate_personalized_opening(
            tenant_id,
            task_id,
            wechat_id,
            # session_id
        )
        # 只返回状态，后续做消息通知
        return {
            "tenant_id": tenant_id,
            "task_id": task_id,
            # "session_id": session_id,
            "status": "success",
            "opening": result["opening"]
        }
    except Exception as e:
        return {
            "tenant_id": tenant_id,
            "task_id": task_id,
            "status": "error",
            "message": str(e)
        }
        # raise HTTPException(status_code=500, detail=f"生成个性化开场白失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "opening_generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11434) 