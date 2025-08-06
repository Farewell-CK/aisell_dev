# 主对话服务 API 文档

## 概述

主对话服务是AI-Sell项目的核心组件，提供智能销售对话功能。支持两种模式：
- **多Agent协作模式** (`main.py`): 响应较慢但更智能，适合生产环境
- **单Agent模式** (`main_v2.py`): 响应更快但拟人化程度较低，适合开发测试

## 服务信息

- **服务名称**: AI Sales Agent Service
- **端口**: 
  - 多Agent模式: 11480
  - 单Agent模式: 11480
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## API 端点

### 1. 处理用户输入

#### 请求信息
- **方法**: `POST`
- **路径**: `/process_user_input`
- **描述**: 处理客户发送的各种类型输入，返回AI销售助手的回复

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，等于user_id，必填
  "belong_chat_id": "string",      // 工作机登录的微信ID，可选
  "wechat_id": "string",           // 客户微信ID，等于session_id，必填
  "session_id": "string",          // 会话ID，等于wechat_id，必填
  "user_input": [                  // 用户输入的各类信息，必填
    {
      "type": "text",              // 输入类型：text/image/video/location
      "content": "你好",           // 文本内容（type为text时）
      "url": "图片URL",            // 文件URL（type为image/video时）
      "local_info": "位置信息",     // 位置信息（type为location时）
      "timestamp": "2025-06-10 10:00:00"  // 时间戳，必填
    }
  ]
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "message": "处理成功",
  "tenant_id": "string",
  "task_id": "string",
  "belong_chat_id": "string",
  "wechat_id": "string",
  "session_id": "string"
}
```

**错误响应** (400/500):
```json
{
  "status": "error",
  "message": "错误描述",
  "error": "详细错误信息"
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:11480/process_user_input" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "wechat_id": "customer_001",
    "session_id": "customer_001",
    "user_input": [
      {
        "type": "text",
        "content": "你好，我想了解一下你们的产品",
        "timestamp": "2025-06-10 10:00:00"
      }
    ]
  }'
```

**响应示例**:
```json
{
  "status": "success",
  "message": "处理成功",
  "tenant_id": "tenant_001",
  "task_id": "task_001",
  "wechat_id": "customer_001",
  "session_id": "customer_001"
}
```

### 2. 删除会话

#### 请求信息
- **方法**: `POST`
- **路径**: `/delete_session`
- **描述**: 删除指定的会话，清理相关数据

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "wechat_id": "string",           // 客户微信ID，必填
  "session_id": "string"           // 会话ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "message": "会话删除成功",
  "tenant_id": "string",
  "task_id": "string",
  "wechat_id": "string",
  "session_id": "string"
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:11480/delete_session" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "wechat_id": "customer_001",
    "session_id": "customer_001"
  }'
```

## 输入类型说明

### 1. 文本输入 (text)
```json
{
  "type": "text",
  "content": "用户输入的文本内容",
  "timestamp": "2025-06-10 10:00:00"
}
```

### 2. 图片输入 (image)
```json
{
  "type": "image",
  "url": "图片文件的URL地址",
  "timestamp": "2025-06-10 10:00:00"
}
```

### 3. 视频输入 (video)
```json
{
  "type": "video",
  "url": "视频文件的URL地址",
  "timestamp": "2025-06-10 10:00:00"
}
```

### 4. 位置输入 (location)
```json
{
  "type": "location",
  "local_info": "位置信息描述",
  "timestamp": "2025-06-10 10:00:00"
}
```

## 性能说明

### 多Agent协作模式 (main.py)
- **响应时间**: 15-30秒
- **特点**: 更智能，支持复杂对话场景

### 单Agent模式 (main_v2.py)
- **响应时间**: 2-6秒
- **特点**: 响应更快，但拟人化程度较低


## 限制说明

- 单次请求的user_input数组长度建议不超过10个
- 图片和视频URL需要可公开访问
