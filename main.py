# main.py
import os
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 导入 agents.py 中的所有内容
from agents import root_agent, session_service, call_agent_async, types
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent Service", description="A service for AI agents to process user requests.")

# 定义请求体模型
class AgentRequest(BaseModel):
    tenant_id: str
    task_id: str
    wechat_id: str
    user_input: str
    # 你可以根据实际需求添加更多字段
    session_id: str | None = None
    other_context: Dict[str, Any] | None = None

# 定义响应体模型
class AgentResponse(BaseModel):
    status: str
    message: str
    output_data: Dict[str, Any] | None = None
    error: str | None = None

@app.post("/process_user_input", response_model=AgentResponse)
async def process_user_input(request: AgentRequest):
    """
    处理用户的输入，通过AI Agent进行多步操作。
    """
    logger.info(f"Received request: {request.dict()}")

    session_id = request.session_id if request.session_id else f"session_{request.tenant_id}_{request.wechat_id}"
    
    # 模拟构建初始事件内容
    # Assuming user_input is text, for image or video you'd parse differently
    initial_event_content = types.parts_pb2.Part(text=request.user_input)

    try:
        # 在这里调用你的root_agent
        # call_agent_async 是你 agents.py 中定义的异步调用函数
        # 需要确保 call_agent_async 能够处理你传递的 context_data
        context_data = {
            "tenant_id": request.tenant_id,
            "task_id": request.task_id,
            "wechat_id": request.wechat_id,
            "other_context": request.other_context,
            "session_id": session_id # 将 session_id 传入上下文
        }
        
        # 使用 AsyncExitStack 来确保 session_service.run_with_session 正确关闭
        async with AsyncExitStack() as stack:
            runner_output = await session_service.run_with_session(
                session_id=session_id,
                agent_name=root_agent.name,  # Pass the agent's name
                agent_input=initial_event_content,
                context_data=context_data,
                callbacks=[root_agent.before_agent_callback] if hasattr(root_agent, 'before_agent_callback') else [],
                runner_factory=lambda: Runner(root_agent, session_service),
                exit_stack=stack, # Pass the AsyncExitStack
            )

        # 提取agent的最终输出
        final_response = runner_output.output.text if runner_output.output and hasattr(runner_output.output, 'text') else "No direct text response from agent."
        
        # 这里你可以根据 runner_output 的结构来提取更多有用的信息
        output_data = {
            "final_agent_response": final_response,
            "all_agent_steps": runner_output.all_steps, # 假设 RunnerOutput 有 all_steps
            "last_tool_output": runner_output.last_tool_output, # 假设 RunnerOutput 有 last_tool_output
        }

        logger.info(f"Agent processing successful for session {session_id}")
        return AgentResponse(
            status="success",
            message="Agent processed your request successfully.",
            output_data=output_data
        )

    except Exception as e:
        logger.error(f"Error processing request for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# 运行 FastAPI 应用
# 在终端中执行: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)