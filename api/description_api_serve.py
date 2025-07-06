from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import os
from utils.file_description import (
    TextSummarizer,
    ImageSummarizer,
    TableSummarizer,
    PPTSummarizer,
    DocumentSummarizer,
    VideoSummarizer
)
from utils.db_insert import update_sale_ai_data_status, insert_sale_ai_data_record, get_task_status, get_last_insert_id
from utils.logger_config import get_api_logger
from dotenv import load_dotenv
import requests
from pathlib import Path
import tempfile
import time
from datetime import datetime
import uuid
import asyncio
from pydantic import BaseModel
import threading

# 获取API服务的日志记录器
logger = get_api_logger()

# 加载环境变量
load_dotenv()

# 获取API密钥
# API_KEY = os.getenv("Ernie_API_KEY", "bce-v3/ALTAK-wKuFEIj8EXZqIDOquAnsT/678c3407baba1a9b64ab889a7f7becd7dc3a4591")
API_KEY = 'bce-v3/ALTAK-cezjDqTjarAi7KJqkjxsf/e821050b6df24c4b721c5dfd5c32f9126dfca856'
if not API_KEY:
    raise ValueError("未找到ERNIE_API_KEY环境变量")
qwen_api_key = os.getenv("Qwen_API_KEY")
if not qwen_api_key:
    raise ValueError("未找到Qwen_API_KEY环境变量")
qwen_base_url = os.getenv("Qwen_BASE_URL")
if not qwen_base_url:
    raise ValueError("未找到Qwen_BASE_URL环境变量")

# 创建FastAPI应用
app = FastAPI(
    title="文件描述API服务",
    description="提供文本、图片、表格、PPT、文档和视频的智能描述服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求ID中间件
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    return response

# 初始化各个总结器
text_summarizer = TextSummarizer(API_KEY)
image_summarizer = ImageSummarizer(API_KEY)
table_summarizer = TableSummarizer(API_KEY)
ppt_summarizer = PPTSummarizer(API_KEY)
document_summarizer = DocumentSummarizer(API_KEY)
video_summarizer = VideoSummarizer(qwen_api_key, qwen_base_url)

# 定义请求模型
class DocumentSummaryRequest(BaseModel):    
    data_id: int
    tenant_id: int
    url: str
    file_type: int  # 0: txt, 1: 图片, 2: 表格, 3: ppt, 4: 视频, 5: pdf/docx

def create_response(data: Any = None, message: str = "success", status: int = 200, request_id: str = None) -> Dict[str, Any]:
    """创建统一的响应格式"""
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id or str(int(time.time() * 1000))
    }

def download_file(url: str) -> str:
    """从URL下载文件到临时目录"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 创建临时文件
        suffix = Path(url).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            return temp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"下载文件失败: {str(e)}")

def process_document_summary(data_id: int, tenant_id: int, url: str, file_type: int):
    """后台处理文档总结任务"""
    try:
        # 更新任务状态为处理中
        update_sale_ai_data_status(data_id, tenant_id, new_ai_status=1, ai_text="处理中...")
        
        # 根据文件类型选择相应的总结器
        if file_type == 0:  # txt
            file_path = download_file(url)
            result = text_summarizer.process_file(file_path)
            os.remove(file_path)
        elif file_type == 1:  # 图片
            file_path = download_file(url)
            result = image_summarizer.summarize_single_image(file_path)
            os.remove(file_path)
        elif file_type == 2:  # 表格
            file_path = download_file(url)
            result = table_summarizer.summarize_table(file_path)
            os.remove(file_path)
        elif file_type == 3:  # ppt
            file_path = download_file(url)
            result = ppt_summarizer.summarize_ppt(file_path)
            os.remove(file_path)
        elif file_type == 4:  # 视频
            result = video_summarizer.summarize_video(url)
            if "视频时发生错误" in result:
                result = "分析视频时发生错误:he video file is too long."
        elif file_type == 5:  # pdf/docx
            file_path = download_file(url)
            result = document_summarizer.summarize_document(file_path)
            os.remove(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        # 更新任务状态为完成
        update_sale_ai_data_status(data_id, tenant_id, new_ai_status=2, ai_text=f"{result}")
        
    except Exception as e:
        # 更新任务状态为失败
        error_message = f"处理失败: {str(e)}"
        update_sale_ai_data_status(data_id, tenant_id, new_ai_status=3, ai_text=error_message)
        logger.error(f"任务 {data_id} 处理失败: {str(e)}", exc_info=True)

@app.post("/api/summarize/document-async")
async def summarize_document_async(request: DocumentSummaryRequest):
    """异步处理文档总结请求"""
    try:
        # 验证文件类型
        if request.file_type not in [0, 1, 2, 3, 4, 5]:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        # 启动后台任务
        thread = threading.Thread(
            target=process_document_summary,
            args=(request.data_id, request.tenant_id, request.url, request.file_type)
        )
        thread.daemon = True
        thread.start()
        
        # 立即返回响应
        return create_response(
            data={
                "id": request.data_id,
                "tenant_id": request.tenant_id,
                "status": 0  # 0: 待处理
            },
            message="任务已提交，正在后台处理"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summarize/status/{task_id}")
async def get_task_status_api(task_id: int, tenant_id: int):
    """获取任务处理状态"""
    try:
        task_info = get_task_status(task_id, tenant_id)
        
        if task_info is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return create_response(
            data={
                "id": task_info["id"],
                "tenant_id": task_info["tenant_id"],
                "status": task_info["status"],
                "ai_text": task_info["ai_text"],
                "create_time": task_info["create_time"],
                "update_time": task_info["update_time"]
            },
            message="查询成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize/text")
async def summarize_text(
    request: Request,
    text_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结文本内容"""
    try:
        file_path = download_file(text_url)
        result = text_summarizer.process_file(file_path)
        update_sale_ai_data_status(record_id=request.state.request_id, tenant_id=request.state.tenant_id, new_ai_status=1, ai_text=result)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/summarize/image")
async def summarize_image(
    request: Request,
    image_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结图片内容"""
    try:
        file_path = download_file(image_url)
        result = image_summarizer.summarize_single_image(file_path, custom_prompt)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/summarize/table")
async def summarize_table(
    request: Request,
    table_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结表格内容"""
    try:
        file_path = download_file(table_url)
        result = table_summarizer.summarize_table(file_path, custom_prompt)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/summarize/ppt")
async def summarize_ppt(
    request: Request,
    ppt_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结PPT内容"""
    try:
        file_path = download_file(ppt_url)
        result = ppt_summarizer.summarize_ppt(file_path, custom_prompt)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/summarize/document")
async def summarize_document(
    request: Request,
    document_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结文档内容"""
    try:
        file_path = download_file(document_url)
        result = document_summarizer.summarize_document(file_path, custom_prompt)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/api/summarize/video")
async def summarize_video(
    request: Request,
    video_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """总结视频内容"""
    try:
        result = video_summarizer.summarize_video(video_url, custom_prompt)
        return create_response(data={"summary": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compare/images")
async def compare_images(
    request: Request,
    image_urls: List[str] = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """比较多张图片"""
    try:
        file_paths = []
        for url in image_urls:
            file_path = download_file(url)
            file_paths.append(file_path)
        
        result = image_summarizer.compare_images(file_paths, custom_prompt)
        return create_response(data={"comparison": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

@app.post("/api/compare/tables")
async def compare_tables(
    request: Request,
    table_urls: List[str] = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """比较多张表格"""
    try:
        file_paths = []
        for url in table_urls:
            file_path = download_file(url)
            file_paths.append(file_path)
        
        result = table_summarizer.compare_tables(file_paths, custom_prompt)
        return create_response(data={"comparison": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

@app.post("/api/compare/ppts")
async def compare_ppts(
    request: Request,
    ppt_urls: List[str] = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """比较多份PPT"""
    try:
        file_paths = []
        for url in ppt_urls:
            file_path = download_file(url)
            file_paths.append(file_path)
        
        result = ppt_summarizer.compare_ppts(file_paths, custom_prompt)
        return create_response(data={"comparison": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

@app.post("/api/compare/documents")
async def compare_documents(
    request: Request,
    document_urls: List[str] = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """比较多份文档"""
    try:
        file_paths = []
        for url in document_urls:
            file_path = download_file(url)
            file_paths.append(file_path)
        
        result = document_summarizer.compare_documents(file_paths, custom_prompt)
        return create_response(data={"comparison": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)

@app.post("/api/compare/videos")
async def compare_videos(
    request: Request,
    video_urls: List[str] = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """比较多段视频"""
    try:
        result = video_summarizer.compare_videos(video_urls, custom_prompt)
        return create_response(data={"comparison": result}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process/directory")
async def process_directory(
    request: Request,
    directory_url: str = Form(...),
    output_file: str = Form(...),
    file_type: str = Form(...)
):
    """处理目录中的文件"""
    try:
        # 下载目录中的所有文件
        file_path = download_file(directory_url)
        
        if file_type == "text":
            text_summarizer.process_file(file_path)
        elif file_type == "image":
            image_summarizer.process_image_directory(file_path, output_file)
        elif file_type == "table":
            table_summarizer.process_directory(file_path, output_file)
        elif file_type == "ppt":
            ppt_summarizer.process_directory(file_path, output_file)
        elif file_type == "document":
            document_summarizer.process_directory(file_path, output_file)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        return create_response(data={"message": "处理完成", "output_file": output_file}, request_id=request.state.request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/test-connection")
async def test_connection(request: Request):
    """
    测试与文心API的连接状态
    """
    try:
        # 使用一个简单的提示词测试API连接
        response = text_summarizer.client.chat.completions.create(
            model="ernie-4.5-turbo-128k",
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'连接测试成功'"}
            ],
            temperature=0.3,
            top_p=0.8
        )
        
        if response.choices[0].message.content:
            return create_response(
                data={
                    "message": "API连接测试成功",
                    "response": response.choices[0].message.content
                },
                request_id=request.state.request_id
            )
        else:
            return create_response(
                data={"message": "API返回空响应"},
                status=500,
                request_id=request.state.request_id
            )
    except Exception as e:
        return create_response(
            data={"message": f"API连接测试失败: {str(e)}"},
            status=500,
            request_id=request.state.request_id
        )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=11431) 