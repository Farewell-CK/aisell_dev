from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from utils.opening_generator import OpeningGenerator, generate_opening

app = FastAPI(title="开场白生成服务", description="自动生成个性化聊天开场白")

# 请求模型
class CustomerInfo(BaseModel):
    name: str
    company: str
    position: Optional[str] = ""
    industry: Optional[str] = ""
    city: Optional[str] = ""

class SalesInfo(BaseModel):
    name: str
    company: str
    product: str
    advantage: Optional[str] = ""
    scenarios: Optional[str] = ""

class EventInfo(BaseModel):
    event_name: str
    event_time: Optional[str] = ""
    event_location: Optional[str] = ""

class ReferrerInfo(BaseModel):
    name: str
    relationship: Optional[str] = "朋友"

class PersonalizedOpeningRequest(BaseModel):
    tenant_id: int
    wechat_id: int
    session_id: str
    # customer_info: CustomerInfo
    # sales_info: SalesInfo
    # context: Optional[str] = ""

class IndustryOpeningRequest(BaseModel):
    industry: str
    customer_info: CustomerInfo
    sales_info: SalesInfo

class EventOpeningRequest(BaseModel):
    event_type: str
    event_info: EventInfo
    customer_info: CustomerInfo
    sales_info: SalesInfo

class ReferralOpeningRequest(BaseModel):
    referrer_info: ReferrerInfo
    customer_info: CustomerInfo
    sales_info: SalesInfo

class MultipleOpeningsRequest(BaseModel):
    customer_info: CustomerInfo
    sales_info: SalesInfo
    opening_types: Optional[List[str]] = None
    context: Optional[str] = ""

# 响应模型
class OpeningResponse(BaseModel):
    tenant_id: int
    task_id: int
    session_id: str
    status: str
    # opening: Optional[str] = None

class MultipleOpeningsResponse(BaseModel):
    tenant_id: int
    task_id: int
    session_id: str
    status: str
    openings: List[OpeningResponse]

@app.get("/")
async def root():
    """服务根路径"""
    return {
        "message": "开场白生成服务",
        "version": "1.0.0",
        "endpoints": [
            "/generate/personalized",
            "/generate/industry", 
            "/generate/event",
            "/generate/referral",
            "/generate/multiple"
        ]
    }

@app.post("/generate/personalized", response_model=OpeningResponse)
async def generate_personalized_opening(request: PersonalizedOpeningRequest):
    """生成个性化开场白"""
    try:
        tenant_id = request.tenant_id
        task_id = request.task_id
        wechat_id = request.wechat_id
        session_id = request.session_id
        generator = OpeningGenerator()
        result = await generator.generate_personalized_opening(
            tenant_id,
            task_id,
            wechat_id,
            session_id
        )
        # 只返回状态，后续做消息通知
        return {
            "tenant_id": tenant_id,
            "task_id": task_id,
            "session_id": session_id,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成个性化开场白失败: {str(e)}")

@app.post("/generate/industry", response_model=OpeningResponse)
async def generate_industry_opening(request: IndustryOpeningRequest):
    """生成行业针对性开场白"""
    try:
        generator = OpeningGenerator()
        result = await generator.generate_industry_opening(
            request.industry,
            request.sales_info.model_dump(),
            request.sales_info.model_dump()
        )
        return OpeningResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成行业开场白失败: {str(e)}")

@app.post("/generate/event", response_model=OpeningResponse)
async def generate_event_opening(request: EventOpeningRequest):
    """生成事件开场白"""
    try:
        generator = OpeningGenerator()
        result = await generator.generate_event_opening(
            request.event_type,
            request.event_info.model_dump(),
            request.sales_info.model_dump()
        )
        return OpeningResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成事件开场白失败: {str(e)}")

@app.post("/generate/referral", response_model=OpeningResponse)
async def generate_referral_opening(request: ReferralOpeningRequest):
    """生成推荐人开场白"""
    try:
        generator = OpeningGenerator()
        result = await generator.generate_referral_opening(
            request.referrer_info.model_dump(),
            request.customer_info.model_dump(),
            request.sales_info.model_dump()
        )
        return OpeningResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成推荐开场白失败: {str(e)}")

@app.post("/generate/multiple", response_model=MultipleOpeningsResponse)
async def generate_multiple_openings(request: MultipleOpeningsRequest):
    """生成多种类型的开场白"""
    try:
        generator = OpeningGenerator()
        result = await generator.generate_multiple_openings(
            request.customer_info.model_dump(),
            request.sales_info.model_dump(),
            request.opening_types
        )
        
        # 转换响应格式
        openings = []
        for opening in result['openings']:
            openings.append(OpeningResponse(**opening))
        
        return MultipleOpeningsResponse(
            status=result['status'],
            openings=openings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成多种开场白失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "opening_generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11434) 