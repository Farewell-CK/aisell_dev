from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from utils.wechat_style_analyzer import WeChatStyleAnalyzer
import logging

app = FastAPI(
    title="微信聊天风格分析服务",
    description="分析微信聊天记录中的说话风格特征",
    version="1.0.0"
)

# 从环境变量获取API密钥
API_KEY = os.getenv("BAIDU_API_KEY", "bce-v3/ALTAK-wKuFEIj8EXZqIDOquAnsT/678c3407baba1a9b64ab889a7f7becd7dc3a4591")
if not API_KEY:
    raise ValueError("请设置环境变量 BAIDU_API_KEY")

analyzer = WeChatStyleAnalyzer(api_key=API_KEY)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "wechat_style_service.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageUrlsRequest(BaseModel):
    image_urls: List[str]

@app.post("/api/analyze")
async def analyze_chat_style(request: ImageUrlsRequest):
    """
    分析微信聊天记录中的说话风格
    
    - **image_urls**: 聊天截图URL列表
    """
    try:
        result = analyzer.analyze_chat_style(request.image_urls)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"} 