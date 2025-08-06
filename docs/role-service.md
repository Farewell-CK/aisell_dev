# 角色创建服务 API 文档

## 概述

角色创建服务提供智能销售角色创建和管理功能，支持异步创建销售角色，并支持多种角色策略。

## 服务信息

- **服务名称**: 角色创建服务
- **端口**: 根据启动脚本配置
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## API 端点

### 1. 创建销售角色 (v1)

#### 请求信息
- **方法**: `POST`
- **路径**: `/create_role`
- **描述**: 异步创建销售角色，立即返回响应，后台处理

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "strategy_id": "string"          // 策略ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "message": "角色创建任务已提交",
  "request_id": "req_123456",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**错误响应** (400/500):
```json
{
  "status": "error",
  "message": "错误描述",
  "request_id": "req_123456",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/create_role" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "strategy_id": "strategy_001"
  }'
```

**响应示例**:
```json
{
  "status": "success",
  "message": "角色创建任务已提交",
  "request_id": "req_123456",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. 创建销售角色 (v2)

#### 请求信息
- **方法**: `POST`
- **路径**: `/create_role_v2`
- **描述**: 异步创建one_to_N销售角色，立即返回响应，后台处理

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "strategy_id": "string"          // 策略ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "message": "角色创建任务已提交",
  "request_id": "req_789012",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/create_role_v2" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "strategy_id": "strategy_001"
  }'
```

