from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Set
import asyncio
from utils.create_role import create_role_background, create_one_to_N_role_background
from utils.logger_config import get_api_logger
import uuid
from datetime import datetime
import threading
import logging
import os

# 获取API服务的日志记录器
logger = get_api_logger()

app = FastAPI(title="角色创建服务", description="异步创建销售角色并立即响应")

# 请求ID中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"收到请求: {request.method} {request.url.path}, 请求ID: {request_id}")
    response = await call_next(request)
    logger.info(f"请求处理完成: {request.method} {request.url.path}, 请求ID: {request_id}, 状态码: {response.status_code}")
    return response

class CreateRoleRequest(BaseModel):
    tenant_id: str
    task_id: str
    strategy_id: str

class CreateRoleResponse(BaseModel):
    status: str
    message: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None

def create_response(data: dict = None, message: str = "success", status: str = "success", request_id: str = None) -> dict:
    """创建统一的响应格式"""
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id
    }

def process_role_creation_background(tenant_id: str, task_id: str, strategy_id: str, request_id: str):
    """后台处理角色创建任务"""
    try:
        logger.info(f"开始后台处理角色创建任务 - 请求ID: {request_id}")
        
        # 创建新的事件循环来运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行角色创建
            loop.run_until_complete(create_role_background(tenant_id, task_id, strategy_id))
            logger.info(f"角色创建任务执行完成 - 请求ID: {request_id}")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"角色创建任务执行失败 - 请求ID: {request_id}, 错误: {str(e)}", exc_info=True)
def process_one_to_N_role_creation_background(tenant_id: str, task_id: str, strategy_id: str, request_id: str):
    """后台处理one_to_N角色创建任务"""
    try:
        logger.info(f"开始后台处理角色创建任务 - 请求ID: {request_id}")
        
        # 创建新的事件循环来运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行角色创建
            loop.run_until_complete(create_one_to_N_role_background(tenant_id, task_id, strategy_id))
            logger.info(f"角色创建任务执行完成 - 请求ID: {request_id}")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"角色创建任务执行失败 - 请求ID: {request_id}, 错误: {str(e)}", exc_info=True)
@app.post("/create_role", response_model=CreateRoleResponse)
async def create_role_api(request: CreateRoleRequest, req: Request):
    """
    创建角色API，收到请求后立即响应，后台线程执行create_role
    """
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(f"开始处理角色创建请求 - 租户ID: {request.tenant_id}, 任务ID: {request.task_id}, 策略ID: {request.strategy_id}, 请求ID: {request_id}")
    
    try:
        # 验证输入参数
        if not request.tenant_id or not request.task_id or not request.strategy_id:
            error_msg = "缺少必要参数: tenant_id, task_id, strategy_id"
            logger.warning(f"参数验证失败: {error_msg}, 请求ID: {request_id}。tenant_id: {request.tenant_id}, task_id: {request.task_id}, strategy_id: {request.strategy_id}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 立即返回响应，后台线程执行角色创建
        logger.info(f"立即返回响应，启动后台线程处理角色创建 - 请求ID: {request_id}")
        
        # 启动后台线程
        thread = threading.Thread(
            target=process_role_creation_background,
            args=(request.tenant_id, request.task_id, request.strategy_id, request_id)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"角色创建任务已提交到后台线程 - 请求ID: {request_id}")
        
        # 立即返回响应
        return create_response(
            data={
                "tenant_id": request.tenant_id,
                "task_id": request.task_id,
                "strategy_id": request.strategy_id,
                "status": "submitted",
                "request_id": request_id
            },
            message="角色创建任务已提交，稍后将通过通知推送结果",
            request_id=request_id
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        error_msg = f"角色创建请求处理失败: {str(e)}"
        logger.error(f"角色创建请求处理失败: {error_msg}, 请求ID: {request_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/create_role_v2", response_model=CreateRoleResponse)
async def create_role_api_v2(request: CreateRoleRequest, req: Request):
    """
    创建角色API，收到请求后立即响应，后台线程执行create_one_to_N_role
    """
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(f"开始处理角色创建请求 - 租户ID: {request.tenant_id}, 任务ID: {request.task_id}, 策略ID: {request.strategy_id}, 请求ID: {request_id}")
    
    try:
        # 验证输入参数
        if not request.tenant_id or not request.task_id or not request.strategy_id:
            error_msg = "缺少必要参数: tenant_id, task_id, strategy_id"
            logger.warning(f"参数验证失败: {error_msg}, 请求ID: {request_id}。tenant_id: {request.tenant_id}, task_id: {request.task_id}, strategy_id: {request.strategy_id}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 立即返回响应，后台线程执行角色创建
        logger.info(f"立即返回响应，启动后台线程处理角色创建 - 请求ID: {request_id}")
        
        # 启动后台线程
        thread = threading.Thread(
            target=process_one_to_N_role_creation_background,
            args=(request.tenant_id, request.task_id, request.strategy_id, request_id)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"角色创建任务已提交到后台线程 - 请求ID: {request_id}")
        
        # 立即返回响应
        return create_response(
            data={
                "tenant_id": request.tenant_id,
                "task_id": request.task_id,
                "strategy_id": request.strategy_id,
                "status": "submitted",
                "request_id": request_id
            },
            message="角色创建任务已提交，稍后将通过通知推送结果",
            request_id=request_id
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        error_msg = f"角色创建请求处理失败: {str(e)}"
        logger.error(f"角色创建请求处理失败: {error_msg}, 请求ID: {request_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check(req: Request):
    """健康检查接口"""
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4()))
    logger.debug(f"健康检查请求 - 请求ID: {request_id}")
    
    return create_response(
        data={
            "service": "create_role_service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        },
        message="服务运行正常",
        request_id=request_id
    )

@app.on_event("startup")
async def startup_event():
    """服务启动事件"""
    logger.info("角色创建服务启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭事件"""
    logger.info("角色创建服务正在关闭") 