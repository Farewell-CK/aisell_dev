# main.py
import os
import json
import asyncio
import threading
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 导入 agents.py 中的所有内容
from google.genai import types # 用于创建消息 Content/Parts
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from agents import root_agent
from utils.chat import call_agent_async
from tools.notify import send_chat
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)
# 为了在控制台看到更多信息，将日志级别设置为 INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库配置信息
DB_URL = "jdbc:mysql://120.77.8.73:9010/sale?useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true&allowMultiQueries=true"
DB_USERNAME = "root"
DB_PASSWORD = "sale159753"

db_url = 'mysql+pymysql://root:sale159753@120.77.8.73:9010/sale'

session_service = DatabaseSessionService(
    db_url=db_url,
    pool_recycle=3600
)

# 初始化 Runner，将 root_agent 与配置好的数据库会话服务关联
runner = Runner(
    app_name="ai_sales_agent",
    agent=root_agent,
    session_service=session_service,
)

app = FastAPI(title="AI Sales Agent Service", description="A service for AI agents to process user requests.")

# 定义请求体模型
class AgentRequest(BaseModel):
    tenant_id: str # 租户id
    task_id: str # 任务id 等于user_id
    belong_chat_id: str | None = None # 工作机登录的微信id
    wechat_id: str # 客户微信id 等于session_id, 工作机微信正在和某个客户聊天, 客户微信id是工作机微信id的客户
    session_id: str # 会话id 等于wechat_id
    user_input: list[dict] # 用户输入的各类信息（文本、图片、视频）
    """
    user_input: list[dict] = [
        {"type": "text", "content": "你好", "timestamp": "2025-06-10 10:00:00"},
        {"type": "image", "url": "www.baidu.com/xxx.jpg", "timestamp": "2025-06-10 10:00:02"},
        {"type": "video", "url": "www.baidu.com/xxx.mp4", "timestamp": "2025-06-10 10:00:03"},
        {"type": "location", "local_info": "位置信息", "timestamp": "2025-06-10 10:00:04"}
    ]
    """
    # 你可以根据实际需求添加更多字段
    # session_id: str | None = None
    # other_context: Dict[str, Any] | None = None

# 定义响应体模型
class AgentResponse(BaseModel):
    status: str
    message: str
    tenant_id: str
    task_id: str
    belong_chat_id: str | None = None
    wechat_id: str
    session_id: str
    # user_input: list[dict]
    # output_data: Dict[str, Any] | None = None
    # error: str | None = None

def process_agent_background(request: AgentRequest):
    """
    后台处理智能体请求的函数
    """
    user_id = request.task_id
    current_session_id = request.session_id
    
    try:
        logger.info(f"开始后台处理请求 - user_id: {user_id}, session_id: {current_session_id}")
        
        # 创建新的事件循环来处理异步操作
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 构建查询字符串，将用户输入转换为更友好的格式
            query_parts = []
            for item in request.user_input:
                timestamp = item.get('timestamp', '')
                if item.get("type") == "text":
                    query_parts.append(f"文本内容: {item.get('content', '')} (时间: {timestamp})")
                elif item.get("type") == "image":
                    query_parts.append(f"图片URL: {item.get('url', '')} (时间: {timestamp})")
                elif item.get("type") == "video":
                    query_parts.append(f"视频URL: {item.get('url', '')} (时间: {timestamp})")
                elif item.get("type") == "location":
                    query_parts.append(f"位置信息: {item.get('local_info', '')} (时间: {timestamp})")
            
            # 将所有输入组合成一个查询字符串
            query = "客户输入信息:\n" + "\n".join(query_parts)
            
            # 调用智能体处理
            agent_response_text = loop.run_until_complete(call_agent_async(
                query=query,
                runner=runner,
                user_id=user_id,
                session_id=current_session_id,
                request_body=request.model_dump()
            ))
            print(f"agent_response_text: {agent_response_text}")
            
            # 尝试解析JSON响应
            try:
                # 移除可能的markdown代码块标记
                cleaned_response = agent_response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                agent_response = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 原始响应: {agent_response_text}")
                # 如果解析失败，创建一个默认的文本响应
                agent_response = {
                    "content_list": [
                        {
                            "type": "text",
                            "content": agent_response_text
                        }
                    ],
                    "collaborate_list": [],
                    "follow_up": {
                        "is_follow_up": 0,
                        "follow_up_content": []
                    }
                }
            
            logger.info(f"智能体处理完成 - user_id: {user_id}, session_id: {current_session_id}")
            
            # 发送通知给后端
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                loop.run_until_complete(send_chat(
                    tenant_id=request.tenant_id,
                    task_id=request.task_id,
                    session_id=request.session_id,
                    belong_chat_id=request.belong_chat_id,
                    chat_content=agent_response
                ))
                logger.info(f"通知发送成功 - user_id: {user_id}, session_id: {current_session_id}")
            except Exception as notify_error:
                logger.error(f"发送通知失败 - user_id: {user_id}, session_id: {current_session_id}, error: {notify_error}")
                
        finally:
            loop.close()
            
    except Exception as e:
        logger.exception(f"后台处理失败 - user_id: {user_id}, session_id: {current_session_id}, error: {e}")
        # 发送错误通知
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(send_chat(
                    tenant_id=request.tenant_id,
                    task_id=request.task_id,
                    session_id=request.session_id,
                    belong_chat_id=request.belong_chat_id,
                    chat_content=f"处理失败: {str(e)}"

                ))
            finally:
                loop.close()
        except Exception as notify_error:
            logger.error(f"发送错误通知失败 - user_id: {user_id}, session_id: {current_session_id}, error: {notify_error}")

@app.post("/process_user_input", response_model=AgentResponse)
async def process_user_input(request: AgentRequest):
    user_id = request.task_id
    current_session_id = request.session_id 
    logger.info(f"收到请求 - user_id: {user_id}, session_id: {current_session_id}")

    try:
        # 使用线程在后台处理任务
        background_thread = threading.Thread(
            target=process_agent_background,
            args=(request,),
            daemon=True  # 设置为守护线程，主程序退出时自动结束
        )
        background_thread.start()
        
        # 立即返回响应，不等待智能体处理完成
        return AgentResponse(
            status="processing",
            message="请求已接收，正在后台处理中。",
            tenant_id=request.tenant_id,
            task_id=request.task_id,
            belong_chat_id=request.belong_chat_id,
            wechat_id=request.wechat_id,
            session_id=request.session_id
        )
    except Exception as e:
        logger.exception(f"处理请求失败 - user_id: {user_id}, session_id: {current_session_id}")
        raise HTTPException(
            status_code=500,
            detail=AgentResponse(
                status="error",
                message="Failed to process request due to an internal error.",
                tenant_id=request.tenant_id,
                task_id=request.task_id,
                belong_chat_id=request.belong_chat_id,
                wechat_id=request.wechat_id,
                session_id=request.session_id
            ).model_dump_json()
        )

# 运行 FastAPI 应用
# 在终端中执行: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11435)