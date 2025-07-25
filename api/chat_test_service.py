from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from utils.chat import  chat_test
from utils.config_loader import ConfigLoader
import os
from prompts.prompts import get_one_to_N_chat_test_prompt
import json
# 配置日志
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "chat_test_service.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="对话测试API服务")

# 加载配置
config = ConfigLoader()
qwen_api_key = config.get_api_key('qwen', 'api_key')

# 定义请求体模型
class MessageContent(BaseModel):
    type: str
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None

class Message(BaseModel):
    role: str
    content: List[MessageContent]

class ChatRequest(BaseModel):
    query: List[Message]
    tenant_id: str
    task_id: str
    session_id: str
    model: str

@app.post("/chat")
async def chat(request: ChatRequest = Body(...)):
    """
    处理聊天请求的API端点
    """
    try: 
        # 使用通义千问模型
        
        system_message = {
                "role": "system",
                "content": [{"type": "text", "text": get_one_to_N_chat_test_prompt(request.tenant_id, request.task_id)}],
            }
        messages = [system_message] + [msg.dict() for msg in request.query]
        print(messages)
        response, assistant_message = await chat_test(qwen_api_key, query=messages)
        print(response)
        json_response = json.loads(response.strip('```json').strip('```'))
        # response = await split_sentence(qwen_api_key, response)
        return {
            "response": json_response,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"} 

