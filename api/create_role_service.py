from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
from utils.create_role import create_role

app = FastAPI(title="角色创建服务", description="异步创建销售角色并立即响应")

class CreateRoleRequest(BaseModel):
    tenant_id: str
    task_id: str

class CreateRoleResponse(BaseModel):
    status: str
    message: Optional[str] = None

@app.post("/create_role", response_model=CreateRoleResponse)
async def create_role_api(request: CreateRoleRequest):
    """
    创建角色API，收到请求后立即响应，异步后台执行create_role
    """
    try:
        # 后台异步执行角色创建
        asyncio.create_task(create_role(request.tenant_id, request.task_id))
        return CreateRoleResponse(status="success", message="角色创建任务已提交，稍后将通过通知推送结果")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色创建失败: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "create_role_service"} 