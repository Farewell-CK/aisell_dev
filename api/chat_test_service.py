from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Optional, List, Dict
import logging
from utils.chat import call_agent_async, chat_qwen, chat_test, split_sentence
from utils.config_loader import ConfigLoader
from utils.chat_history import ChatHistory
from utils.db_queries import select_sale_prompt
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="对话测试API服务")

# 加载配置
config = ConfigLoader()
qwen_api_key = config.get_api_key('qwen', 'api_key')

# 初始化聊天历史管理器
chat_history = ChatHistory()

# 请求模型
class ChatRequest(BaseModel):
    query: str
    tenant_id: str
    task_id: str
    session_id: str
    model: Optional[str] = "qwen"

# 响应模型
class ChatResponse(BaseModel):
    response: list[str]
    status: str
    history: Optional[List[Dict]] = None

class UpdateSalePromptRequest(BaseModel):
    tenant_id : str
    task_id : str
    update_prompt : str

@app.post("/api/update_sale_prompt")
async def update_sale_prompt(request : UpdateSalePromptRequest):
    """
    更新销售提示词
    """
    try:
        # update_sale_prompt(request.tenant_id, request.task_id, request.update_prompt)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"更新销售提示词失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理聊天请求的API端点
    """
    try:
        # 加载历史记录
        history = chat_history.load_history(
            request.tenant_id, 
            request.task_id, 
            request.session_id
        )
        
        # 构建带有历史记录的提示词
        formatted_history = chat_history.get_formatted_history(
            request.tenant_id, 
            request.task_id, 
            request.session_id
        )
        
        # 构建完整的提示词
        full_prompt = f"{formatted_history}\n用户: {request.query}\nAI: " if formatted_history else request.query

        if request.model == "qwen":
            # 使用通义千问模型
            system_prompt = select_sale_prompt(request.tenant_id, request.task_id)
            response = await chat_test(qwen_api_key, system_prompt, full_prompt)
            response = await split_sentence(qwen_api_key, response)
            # 保存对话历史
            chat_history.save_history(
                request.tenant_id,
                request.task_id,
                request.session_id,
                request.query,
                '\n'.join(response)
            )
            
            return ChatResponse(
                response=response,
                status="success",
                history=history
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的模型类型")
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{tenant_id}/{task_id}/{session_id}")
async def get_history(tenant_id: str, task_id: str, session_id: str):
    """
    获取指定会话的历史记录
    """
    try:
        history = chat_history.load_history(tenant_id, task_id, session_id)
        return {"history": history, "status": "success"}
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{tenant_id}/{task_id}/{session_id}")
async def clear_history(tenant_id: str, task_id: str, session_id: str):
    """
    清除指定会话的历史记录
    """
    try:
        file_path = chat_history._get_history_file_path(tenant_id, task_id, session_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"status": "success", "message": "历史记录已清除"}
    except Exception as e:
        logger.error(f"清除历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy"} 

