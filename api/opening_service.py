from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from utils.opening_generator import OpeningGenerator, generate_opening
import logging
import os
from utils.festival_utils import generate_festival_greetings
from utils.customer_maintenance_utils import generate_customer_maintenance_message
from utils.wechat_greeting_utils import generate_wechat_greeting_message
import json

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



class ReferrerInfo(BaseModel):
    name: str
    relationship: Optional[str] = "朋友"

class PersonalizedOpeningRequest(BaseModel):
    tenant_id: str
    wechat_id: str
    task_id: str
# 响应模型
class OpeningResponse(BaseModel):
    tenant_id: str
    task_id: str
    status: str
    message: Optional[list[str]] = None

class FestivalGreetingRequest(BaseModel):
    date: str  # 格式：2024-06-10
    tenant_id: str
    task_id: str
    wechat_id: str

class FestivalGreetingResponse(BaseModel):
    status: str
    festival: str
    greetings: list[str]

class CustomerMaintenanceRequest(BaseModel):
    tenant_id: str
    task_id: str

class CustomerMaintenanceResponse(BaseModel):
    status: str
    messages: list[str]

class WechatGreetingRequest(BaseModel):
    tenant_id: str
    task_id: str
    wechat_id: str

class WechatGreetingResponse(BaseModel):
    status: str
    messages: list[str]


@app.get("/")
async def root():
    """服务根路径"""
    return {
        "message": "开场白生成服务",
        "version": "1.0.0",
        "endpoints": [
            "/generate/personalized",
            "/generate/festival_greeting",
            "/generate/customer_maintenance",
            "/generate/wechat_greeting",
        ]
    }

@app.post("/generate/personalized")
async def generate_personalized_opening(request: PersonalizedOpeningRequest):
    """生成个性化开场白"""
    try:
        tenant_id = request.tenant_id
        task_id = request.task_id
        wechat_id = request.wechat_id
        # session_id = request.session_id
        generator = OpeningGenerator()
        logger.info(f"开始生成个性化开场白: {tenant_id}, {task_id}, {wechat_id}")
        result = await generator.generate_personalized_opening(
            tenant_id,
            task_id,
            wechat_id,
            # session_id
        )
        logger.info(f"个性化开场白生成成功: {result}")
        # 只返回状态，后续做消息通知
        return {
            "tenant_id": tenant_id,
            "task_id": task_id,
            # "session_id": session_id,
            "status": "success",
            "message": result["opening"]
        }
    except Exception as e:
        return {
            "tenant_id": tenant_id,
            "task_id": task_id,
            "status": "error",
            "message": str(e)
        }
        # raise HTTPException(status_code=500, detail=f"生成个性化开场白失败: {str(e)}")

@app.post("/generate/festival_greeting", response_model=FestivalGreetingResponse)
async def generate_festival_greeting(request: FestivalGreetingRequest):
    """生成节日问候语"""
    try:
        # 获取公司信息，参考opening_generator.py
        from utils.db_queries import select_knowledge
        company_info = select_knowledge(request.tenant_id, request.task_id)
        # 简单提取公司名（假设公司名在company_info字符串前20字内）
        # match = re.search(r"[\u4e00-\u9fa5A-Za-z0-9]{2,20}", company_info)
        # company = match.group(0) if match else "本公司"
        festival, greetings = await generate_festival_greetings(request.date, company_info)
        return {
            "status": "success",
            "festival": festival,
            # "greetings": json.loads(greetings.strip("```json").strip("```").strip())
            "greetings": greetings
        }
    except Exception as e:
        return {
            "status": "error",
            "festival": "",
            "greetings": [f"生成节日问候失败: {str(e)}"]
        }

@app.post("/generate/customer_maintenance", response_model=CustomerMaintenanceResponse)
async def generate_customer_maintenance(request: CustomerMaintenanceRequest):
    """生成客情维护话术"""
    try:
        logger.info(f"开始生成客情维护话术: {request.tenant_id}, {request.task_id}")
        status, messages = await generate_customer_maintenance_message(
            request.tenant_id, 
            request.task_id
        )
        logger.info(f"客情维护话术生成成功: {status}")
        return {
            "status": status,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"生成客情维护话术失败: {str(e)}")
        return {
            "status": "error",
            "messages": [f"生成客情维护话术失败: {str(e)}"]
        }

@app.post("/generate/wechat_greeting", response_model=WechatGreetingResponse)
async def generate_wechat_greeting(request: WechatGreetingRequest):
    """生成微信添加好友时的打招呼话术"""
    try:
        logger.info(f"开始生成微信打招呼话术: {request.tenant_id}, {request.task_id}, {request.wechat_id}")
        status, messages = await generate_wechat_greeting_message(
            request.tenant_id, 
            request.task_id,
            request.wechat_id
        )
        logger.info(f"微信打招呼话术生成成功: {status}")
        return {
            "status": status,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"生成微信打招呼话术失败: {str(e)}")
        return {
            "status": "error",
            "messages": [f"生成微信打招呼话术失败: {str(e)}"]
        }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "opening_generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11434) 