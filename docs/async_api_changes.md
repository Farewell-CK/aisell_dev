# 异步文档总结API修改总结

## 概述

根据您的需求，我已经将原有的同步文档总结API改造为异步处理模式。现在API支持后台任务处理，可以立即返回响应，避免长时间等待。

## 主要修改

### 1. API服务修改 (`api/description_api_serve.py`)

#### 新增功能：
- **异步任务处理**: 添加了 `process_document_summary` 函数，在后台线程中处理文档总结
- **新的API端点**: 
  - `POST /api/summarize/document-async` - 提交异步文档总结任务
  - `GET /api/summarize/status/{task_id}` - 查询任务状态
- **请求模型**: 定义了 `DocumentSummaryRequest` 模型，包含 `id`, `tenant_id`, `url`, `file_type` 字段

#### 文件类型支持：
- `0`: 文本文件 (.txt)
- `1`: 图片文件 (.jpg, .png, .gif等)
- `2`: 表格文件 (.xlsx, .xls, .csv等)
- `3`: PPT文件 (.pptx, .ppt)
- `4`: 视频文件 (.mp4, .avi, .mov等)
- `5`: 文档文件 (.pdf, .docx)

#### 任务状态：
- `0`: 待处理 - 任务已提交，等待处理
- `1`: 已完成 - 任务处理完成，可以获取结果
- `2`: 处理中 - 任务正在后台处理
- `3`: 处理失败 - 任务处理失败，可以查看错误信息

### 2. 数据库工具增强 (`utils/db_insert.py`)

#### 新增函数：
- `get_task_status(record_id, tenant_id)` - 查询任务处理状态
- `get_last_insert_id()` - 获取最后插入记录的ID

### 3. 数据库管理器增强 (`tools/database.py`)

#### 新增方法：
- `fetch_one(query, params)` - 执行查询并返回单条记录
- `fetch_all(query, params)` - 执行查询并返回所有记录

## 新增文件

### 1. 启动脚本 (`run_async_description_service.py`)
```python
# 启动异步文档总结API服务
python run_async_description_service.py
```

### 2. 测试脚本 (`test_async_api.py`)
```python
# 测试异步API功能
python test_async_api.py
```

### 3. 使用示例 (`example_usage.py`)
```python
# 演示如何使用异步API
python example_usage.py
```

### 4. 文档 (`docs/async_document_summary_api.md`)
详细的API使用说明，包括：
- API端点说明
- 请求/响应格式
- 示例代码（Python和JavaScript）
- 注意事项和错误处理

## API使用流程

### 1. 提交任务
```bash
curl -X POST "http://localhost:11431/api/summarize/document-async" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 12345,
    "tenant_id": 1,
    "url": "https://example.com/document.pdf",
    "file_type": 5
  }'
```

**响应**:
```json
{
  "status": 200,
  "message": "任务已提交，正在后台处理",
  "data": {
    "id": 67890,
    "tenant_id": 1,
    "status": 0
  }
}
```

### 2. 查询状态
```bash
curl "http://localhost:11431/api/summarize/status/67890?tenant_id=1"
```

**响应**:
```json
{
  "status": 200,
  "message": "查询成功",
  "data": {
    "id": 67890,
    "tenant_id": 1,
    "status": 1,
    "ai_text": "文档总结内容...",
    "create_time": "2024-01-01T12:00:00",
    "update_time": "2024-01-01T12:05:00"
  }
}
```

## 技术特点

### 1. 异步处理
- 使用Python的 `threading` 模块实现后台任务处理
- 立即返回响应，避免客户端长时间等待
- 支持并发处理多个任务

### 2. 状态管理
- 完整的任务状态跟踪（待处理、处理中、已完成、失败）
- 数据库持久化存储任务状态和结果
- 支持状态查询和结果获取

### 3. 错误处理
- 完善的异常处理机制
- 任务失败时记录错误信息
- 支持任务重试和状态恢复

### 4. 扩展性
- 模块化设计，易于添加新的文件类型支持
- 支持自定义提示词和参数
- 可配置的处理参数

## 部署说明

### 1. 环境要求
- Python 3.7+
- FastAPI
- uvicorn
- 数据库（MySQL/PostgreSQL）
- 相关依赖包（见 requirements.txt）

### 2. 配置
- 数据库配置：`configs/database.yaml`
- API密钥配置：环境变量或配置文件
- 服务端口：默认11431，可通过环境变量配置

### 3. 启动服务
```bash
# 方式1：使用启动脚本
python run_async_description_service.py

# 方式2：直接使用uvicorn
uvicorn api.description_api_serve:app --host 0.0.0.0 --port 11431

# 方式3：使用环境变量配置
HOST=0.0.0.0 PORT=11431 RELOAD=true python run_async_description_service.py
```

## 监控和维护

### 1. 日志监控
- 服务启动日志
- 任务处理日志
- 错误日志记录

### 2. 性能监控
- 任务处理时间
- 并发任务数量
- 系统资源使用情况

### 3. 数据库维护
- 定期清理已完成的任务记录
- 监控数据库连接池状态
- 备份重要数据

## 注意事项

1. **文件URL**: 确保提供的文件URL是可访问的
2. **文件大小**: 建议单个文件不超过100MB
3. **并发限制**: 根据服务器性能调整并发数量
4. **超时设置**: 建议设置合理的任务超时时间
5. **错误处理**: 客户端需要处理网络错误和任务失败情况
6. **状态轮询**: 建议使用5-10秒的轮询间隔

## 后续优化建议

1. **任务队列**: 使用Redis或RabbitMQ实现更可靠的任务队列
2. **负载均衡**: 支持多实例部署和负载均衡
3. **缓存机制**: 对相同文件的总结结果进行缓存
4. **进度反馈**: 支持任务处理进度的实时反馈
5. **批量处理**: 支持批量提交多个文档总结任务
6. **WebSocket**: 使用WebSocket实现实时状态推送 