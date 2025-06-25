from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from utils.wechat_style_analyzer import WeChatStyleAnalyzer

app = FastAPI(
    title="微信聊天风格分析服务",
    description="分析微信聊天记录中的说话风格特征",
    version="1.0.0"
)

# 从环境变量获取API密钥
API_KEY = os.getenv("BAIDU_API_KEY")
if not API_KEY:
    raise ValueError("请设置环境变量 BAIDU_API_KEY")

analyzer = WeChatStyleAnalyzer(api_key=API_KEY)

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