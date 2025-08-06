# 文件描述服务 API 文档

## 概述

文件描述服务提供智能文件分析和描述功能，支持文本、图片、表格、PPT、文档和视频的智能描述和总结。

## 服务信息

- **服务名称**: 文件描述API服务
- **端口**: 根据启动脚本配置
- **协议**: HTTP/HTTPS
- **数据格式**: JSON/Form Data

## API 端点

### 1. 异步文档总结

#### 请求信息
- **方法**: `POST`
- **路径**: `/api/summarize/document-async`
- **描述**: 异步处理文档总结任务，立即返回任务ID

#### 请求参数

**请求体** (JSON):
```json
{
  "data_id": 123,              // 数据ID，必填
  "tenant_id": 456,            // 租户ID，必填
  "url": "文件URL",            // 文件URL，必填
  "file_type": 0               // 文件类型，必填
}
```

**文件类型说明**:
- `0`: 文本文件 (txt)
- `1`: 图片文件 (jpg, png, gif等)
- `2`: 表格文件 (xlsx, csv等)
- `3`: PPT文件 (pptx)
- `4`: 视频文件 (mp4, avi等)
- `5`: 文档文件 (pdf, docx)

#### 响应参数

**成功响应** (200):
```json
{
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id or str(int(time.time() * 1000))
    }
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/summarize/document-async" \
  -H "Content-Type: application/json" \
  -d '{
    "data_id": 123,
    "tenant_id": 456,
    "url": "https://example.com/document.pdf",
    "file_type": 5
  }'
```

### 2. 获取任务状态

#### 请求信息
- **方法**: `GET`
- **路径**: `/api/summarize/status/{task_id}`
- **描述**: 查询异步任务的处理状态和结果

#### 请求参数

**路径参数**:
- `task_id`: 任务ID，从异步接口返回

**查询参数**:
- `tenant_id`: 租户ID，必填

#### 响应参数

**处理中** (200):
```json
{
  "status": 200,
  "message": "任务处理中",
  "data": {
    "task_id": 789,
    "status": "processing",
    "progress": 50
  }
}
```

**处理完成** (200):
```json
{
  "status": 200,
  "message": "任务完成",
  "data": {
    "task_id": 789,
    "status": "completed",
    "result": "文件描述内容",
    "summary": "文件总结"
  }
}
```
