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
from one_agents import one_to_N_agent
from utils.chat import call_agent_async
from tools.notify import send_chat
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)
# 为了在控制台看到更多信息，将日志级别设置为 INFO
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库配置信息
DB_URL = "jdbc:mysql://127.0.0.1:3306/sale?useUnicode=true&characterEncoding=utf-8&useSSL=false&allowPublicKeyRetrieval=true&allowMultiQueries=true"
DB_USERNAME = "root"
DB_PASSWORD = "123456"

db_url = 'mysql+pymysql://root:123456@127.0.0.1:3306/sale'

session_service = DatabaseSessionService(
    db_url=db_url,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,  # 建立连接的超时时间（秒）
        "read_timeout": 30,     # 读取数据的超时时间（秒）
        "write_timeout": 30     # 写入数据的超时时间（秒）
    },
)

# 初始化 Runner，将 root_agent 与配置好的数据库会话服务关联
runner = Runner(
    app_name="ai_sales_agent_v2",
    agent=one_to_N_agent,
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

    def parse_agent_response(agent_response_text):
        """
        解析智能体返回的文本，返回list[dict]或dict
        支持以下情况：
        1. 只包含json代码块
        2. 普通文本+json代码块
        3. 多个json代码块
        4. 只包含普通文本（无法json解析时忽略）
        """
        import re
        responses = []
        # 匹配所有 ```json ... ``` 代码块
        json_blocks = re.findall(r"```json(.*?)```", agent_response_text, re.DOTALL)
        if json_blocks:
            for block in json_blocks:
                cleaned = block.strip()
                if not cleaned:
                    continue
                try:
                    responses.append(json.loads(cleaned))
                except Exception as e:
                    logger.error(f"JSON解析失败: {e}, 原始响应: {cleaned}")
        else:
            # 没有代码块，尝试整体解析
            cleaned = agent_response_text.strip()
            # 去除多余的反引号
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            if cleaned:
                try:
                    responses.append(json.loads(cleaned))
                except Exception as e:
                    logger.error(f"JSON解析失败: {e}, 原始响应: {cleaned}")
        return responses

    def send_notify(agent_response):
        """
        发送通知
        """
        try:
            asyncio.run(send_chat(
                tenant_id=request.tenant_id,
                task_id=request.task_id,
                session_id=request.session_id,
                belong_chat_id=request.belong_chat_id,
                chat_content=agent_response
            ))
            logger.info(f"通知发送成功 - user_id: {user_id}, session_id: {current_session_id}")
        except Exception as notify_error:
            logger.error(f"发送通知失败 - user_id: {user_id}, session_id: {current_session_id}, error: {notify_error}")

    try:
        logger.info(f"开始后台处理请求 - user_id: {user_id}, session_id: {current_session_id}")

        # 构建查询字符串
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
            elif item.get("type") == "file":
                query_parts.append(f"文件内容: {item.get('content', '')} (时间: {timestamp})")
            elif item.get("type") == "cite":
                cite_content = json.loads(item.get('content', '{}'))
                query_parts.append(f"对这条信息：{cite_content.get('content', '')} 的回复：{cite_content.get('title', '')} (时间: {timestamp})")
        query = "客户输入信息:\n" + "\n".join(query_parts)

        # 调用智能体处理
        agent_response_text = asyncio.run(call_agent_async(
            query=query,
            runner=runner,
            user_id=user_id,
            session_id=current_session_id,
            request_body=request.model_dump()
        ))

        responses = parse_agent_response(agent_response_text)
        if not responses:
            # 解析失败，发送默认消息
            agent_response = {
                "content_list": [
                    {"type": "text", "content": "🤔"}
                ],
                "collaborate_list": [],
                "follow_up": {
                    "is_follow_up": 0,
                    "follow_up_content": []
                }
            }
            send_notify(agent_response)
        else:
            for agent_response in responses:
                send_notify(agent_response)

        logger.info(f"智能体处理完成 - user_id: {user_id}, session_id: {current_session_id}")

    except Exception as e:
        logger.exception(f"后台处理失败 - user_id: {user_id}, session_id: {current_session_id}, error: {e}")
        # 发送错误通知
        try:
            error_msg = "🤔，让我想想"
            asyncio.run(send_chat(
                tenant_id=request.tenant_id,
                task_id=request.task_id,
                session_id=request.session_id,
                belong_chat_id=request.belong_chat_id,
                chat_content=error_msg
            ))
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

@app.post("/delete_session", response_model=AgentResponse)
async def delete_session(request: AgentRequest):
    session_id = request.session_id
    try:
        #先检查是否存在
        if session_service.get_session(
            app_name="ai_sales_agent_v2",
            user_id=request.task_id,
            session_id=session_id+request.task_id
        ):
            logger.info(f"会话已存在 - session_id: {session_id}，开始删除")
        else:
            logger.info(f"会话不存在 - session_id: {session_id}，不删除")
        session_service.delete_session(
            app_name="ai_sales_agent_v2",
            user_id=request.task_id,
            session_id=session_id+request.task_id
        )
        logger.info(f"删除会话成功 - session_id: {session_id}")
        # 检查是否删除成功
        if session_service.get_session(
            app_name="ai_sales_agent_v2",
            user_id=request.task_id,
            session_id=session_id+request.task_id
        ):
            logger.info(f"经检查，会话已删除 - session_id: {session_id}")
        else:
            logger.info(f"经检查，会话未删除 - session_id: {session_id}")
        return AgentResponse(
            status="success",
            message="Session deleted successfully.",
            tenant_id=request.tenant_id,
            task_id=request.task_id,
            belong_chat_id=request.belong_chat_id,
            wechat_id=request.wechat_id,
            session_id=request.session_id
        )
    except Exception as e:
        logger.exception(f"删除会话失败 - session_id: {session_id}, error: {e}")
        raise HTTPException(
            status_code=500,
            detail=AgentResponse(
                status="error",
                message="Failed to delete session due to an internal error.",
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
    # 11480 将一直设置为测试端口
    uvicorn.run(app, host="0.0.0.0", port=11480)