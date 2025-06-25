# 异步文档总结API使用说明

## 概述

异步文档总结API提供了文档总结的异步处理功能，支持多种文件类型的智能总结，包括文本、图片、表格、PPT、视频和PDF/DOCX文档。

## API端点

### 1. 提交异步文档总结任务

**端点**: `POST /api/summarize/document-async`

**请求体**:
```json
{
    "id": 12345,           // 请求ID（可选，实际使用数据库生成的ID）
    "tenant_id": 1,        // 租户ID
    "url": "https://example.com/document.pdf",  // 文档URL
    "file_type": 5         // 文件类型
}
```

**文件类型说明**:
- `0`: 文本文件 (.txt)
- `1`: 图片文件 (.jpg, .png, .gif等)
- `2`: 表格文件 (.xlsx, .xls, .csv等)
- `3`: PPT文件 (.pptx, .ppt)
- `4`: 视频文件 (.mp4, .avi, .mov等)
- `5`: 文档文件 (.pdf, .docx)

**响应示例**:
```json
{
    "status": 200,
    "message": "任务已提交，正在后台处理",
    "data": {
        "id": 67890,       // 数据库生成的任务ID
        "tenant_id": 1,
        "status": 0        // 任务状态：0-待处理
    },
    "timestamp": "2024-01-01T12:00:00",
    "request_id": "abc123"
}
```

### 2. 查询任务状态

**端点**: `GET /api/summarize/status/{task_id}?tenant_id={tenant_id}`

**参数**:
- `task_id`: 任务ID（路径参数）
- `tenant_id`: 租户ID（查询参数）

**响应示例**:
```json
{
    "status": 200,
    "message": "查询成功",
    "data": {
        "id": 67890,
        "tenant_id": 1,
        "status": 1,       // 任务状态
        "ai_text": "文档总结内容...",
        "create_time": "2024-01-01T12:00:00",
        "update_time": "2024-01-01T12:05:00"
    },
    "timestamp": "2024-01-01T12:05:00",
    "request_id": "def456"
}
```

## 任务状态说明

- `0`: 待处理 - 任务已提交，等待处理
- `1`: 已完成 - 任务处理完成，可以获取结果
- `2`: 处理中 - 任务正在后台处理
- `3`: 处理失败 - 任务处理失败，可以查看错误信息

## 使用流程

1. **提交任务**: 调用 `POST /api/summarize/document-async` 提交文档总结任务
2. **获取任务ID**: 从响应中获取数据库生成的任务ID
3. **轮询状态**: 定期调用 `GET /api/summarize/status/{task_id}` 查询任务状态
4. **获取结果**: 当状态为 `1`（已完成）时，从响应中获取总结结果

## 示例代码

### Python示例

```python
import requests
import time

def submit_document_summary(tenant_id, url, file_type):
    """提交文档总结任务"""
    data = {
        "id": 12345,
        "tenant_id": tenant_id,
        "url": url,
        "file_type": file_type
    }
    
    response = requests.post(
        "http://localhost:11431/api/summarize/document-async",
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["data"]["id"]
    else:
        raise Exception(f"提交任务失败: {response.text}")

def get_task_status(task_id, tenant_id):
    """查询任务状态"""
    response = requests.get(
        f"http://localhost:11431/api/summarize/status/{task_id}",
        params={"tenant_id": tenant_id}
    )
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"查询状态失败: {response.text}")

def wait_for_completion(task_id, tenant_id, max_wait=300):
    """等待任务完成"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_data = get_task_status(task_id, tenant_id)
        
        if status_data["status"] == 1:  # 已完成
            return status_data["ai_text"]
        elif status_data["status"] == 3:  # 处理失败
            raise Exception(f"任务处理失败: {status_data['ai_text']}")
        
        time.sleep(5)  # 等待5秒后再次查询
    
    raise Exception("任务超时")

# 使用示例
try:
    # 提交PDF文档总结任务
    task_id = submit_document_summary(
        tenant_id=1,
        url="https://example.com/document.pdf",
        file_type=5
    )
    
    print(f"任务已提交，ID: {task_id}")
    
    # 等待任务完成
    result = wait_for_completion(task_id, 1)
    print(f"总结结果: {result}")
    
except Exception as e:
    print(f"错误: {e}")
```

### JavaScript示例

```javascript
async function submitDocumentSummary(tenantId, url, fileType) {
    const response = await fetch('http://localhost:11431/api/summarize/document-async', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: 12345,
            tenant_id: tenantId,
            url: url,
            file_type: fileType
        })
    });
    
    const result = await response.json();
    if (response.ok) {
        return result.data.id;
    } else {
        throw new Error(`提交任务失败: ${result.message}`);
    }
}

async function getTaskStatus(taskId, tenantId) {
    const response = await fetch(
        `http://localhost:11431/api/summarize/status/${taskId}?tenant_id=${tenantId}`
    );
    
    const result = await response.json();
    if (response.ok) {
        return result.data;
    } else {
        throw new Error(`查询状态失败: ${result.message}`);
    }
}

async function waitForCompletion(taskId, tenantId, maxWait = 300000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWait) {
        const statusData = await getTaskStatus(taskId, tenantId);
        
        if (statusData.status === 1) { // 已完成
            return statusData.ai_text;
        } else if (statusData.status === 3) { // 处理失败
            throw new Error(`任务处理失败: ${statusData.ai_text}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 5000)); // 等待5秒
    }
    
    throw new Error('任务超时');
}

// 使用示例
async function main() {
    try {
        // 提交PDF文档总结任务
        const taskId = await submitDocumentSummary(
            1,
            'https://example.com/document.pdf',
            5
        );
        
        console.log(`任务已提交，ID: ${taskId}`);
        
        // 等待任务完成
        const result = await waitForCompletion(taskId, 1);
        console.log(`总结结果: ${result}`);
        
    } catch (error) {
        console.error(`错误: ${error.message}`);
    }
}

main();
```

## 注意事项

1. **文件URL**: 确保提供的文件URL是可访问的，支持HTTP/HTTPS协议
2. **文件大小**: 建议单个文件不超过100MB
3. **并发限制**: 系统支持并发处理多个任务，但建议控制并发数量
4. **超时处理**: 建议设置合理的超时时间，避免长时间等待
5. **错误处理**: 注意处理网络错误、文件下载失败等异常情况
6. **状态轮询**: 建议使用5-10秒的轮询间隔，避免过于频繁的请求

## 错误码说明

- `400`: 请求参数错误（如不支持的文件类型）
- `404`: 任务不存在
- `500`: 服务器内部错误

## 支持的文件格式

### 文本文件 (file_type: 0)
- .txt, .md, .log

### 图片文件 (file_type: 1)
- .jpg, .jpeg, .png, .gif, .bmp, .webp

### 表格文件 (file_type: 2)
- .xlsx, .xls, .csv

### PPT文件 (file_type: 3)
- .pptx, .ppt

### 视频文件 (file_type: 4)
- .mp4, .avi, .mov, .wmv, .flv, .webm

### 文档文件 (file_type: 5)
- .pdf, .docx, .doc 