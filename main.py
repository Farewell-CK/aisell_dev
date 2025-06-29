# main.py
import os
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 导入 agents.py 中的所有内容
from google.genai import types # 用于创建消息 Content/Parts
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from agents import root_agent
from utils.chat import call_agent_async
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)
# 为了在控制台看到更多信息，将日志级别设置为 INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库配置信息
DB_URL = "jdbc:mysql://120.77.8.73:9010/sale?useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true&allowMultiQueries=true"
DB_USERNAME = "root"
DB_PASSWORD = "sale159753"

session_service = DatabaseSessionService(
    db_url=DB_URL,
    username=DB_USERNAME,
    password=DB_PASSWORD,
)

# 初始化 Runner，将 root_agent 与配置好的数据库会话服务关联
runner = Runner(
    root_agent,
    session_service=session_service,
)

app = FastAPI(title="AI Agent Service", description="A service for AI agents to process user requests.")

# 定义请求体模型
class AgentRequest(BaseModel):
    tenant_id: str
    task_id: str
    belong_chat_id: str | None = None # 工作机登录的微信id
    wechat_id: str
    user_input: str
    # 你可以根据实际需求添加更多字段
    session_id: str | None = None
    # other_context: Dict[str, Any] | None = None

# 定义响应体模型
class AgentResponse(BaseModel):
    status: str
    message: str
    output_data: Dict[str, Any] | None = None
    error: str | None = None

@app.post("/process_user_input", response_model=AgentResponse)
async def process_user_input(request: AgentRequest):
    user_id = request.task_id
    current_session_id = request.session_id 
    logger.info(f"Received request for user_id: {user_id}, session_id: {current_session_id}")

    try:
        agent_response_text = await call_agent_async(
            query=request.user_input,
            runner=runner,
            user_id=user_id,
            session_id=current_session_id,
            request_body=request.model_dump() # 传递整个请求体
        )

        return AgentResponse(
            status="success",
            message="Agent processed the request successfully.",
            output_data={"agent_text_response": agent_response_text}
        )
    except Exception as e:
        logger.exception(f"Error processing request for user_id: {user_id}, session_id: {current_session_id}")
        raise HTTPException(
            status_code=500,
            detail=AgentResponse(
                status="error",
                message="Failed to process request due to an internal error.",
                error=str(e)
            ).model_dump_json()
        )

# 运行 FastAPI 应用
# 在终端中执行: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)