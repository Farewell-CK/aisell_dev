# 开场白生成服务 API 文档

## 概述

开场白生成服务提供智能开场白和问候语生成功能，支持个性化开场白、节日问候、客户维护消息等多种场景。

## 服务信息

- **服务名称**: 开场白生成服务
- **端口**: 根据启动脚本配置
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## API 端点

### 1. 生成个性化开场白

#### 请求信息
- **方法**: `POST`
- **路径**: `/generate/personalized`
- **描述**: 根据客户信息和公司资料生成个性化开场白

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "wechat_id": "string"            // 客户微信ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "tenant_id": "string",
  "task_id": "string",
  "status": "success",
  "message": ["开场白1", "开场白2", "开场白3"]
}
```

**错误响应** (400/500):
```json
{
  "status": "error",
  "message": "错误描述"
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/generate/personalized" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "wechat_id": "customer_001"
  }'
```

**响应示例**:
```json
{
  "tenant_id": "tenant_001",
  "task_id": "task_001",
  "status": "success",
  "message": [
    "您好！我是XX公司的销售顾问，很高兴认识您。我们公司专注于提供高质量的解决方案，希望能为您带来价值。",
    "Hi！我是XX公司的专业顾问，看到您的资料很感兴趣。我们有很多成功案例，想和您分享一下。",
    "您好！我是XX公司的销售代表，我们公司在这个领域有丰富的经验，希望能为您提供专业的服务。"
  ]
}
```

### 2. 生成节日问候

#### 请求信息
- **方法**: `POST`
- **路径**: `/generate/festival_greeting`
- **描述**: 根据指定日期生成节日问候语

#### 请求参数

**请求体** (JSON):
```json
{
  "date": "2024-06-10",           // 日期，格式：YYYY-MM-DD，必填
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "wechat_id": "string"            // 客户微信ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "festival": "端午节",
  "greetings": [
    "端午节快乐！祝您身体健康，万事如意！",
    "端午安康！愿您在这个传统佳节里阖家欢乐！",
    "祝您端午节快乐，粽子香甜，生活美满！"
  ]
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/generate/festival_greeting" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-06-10",
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "wechat_id": "customer_001"
  }'
```

### 3. 生成客户维护消息

#### 请求信息
- **方法**: `POST`
- **路径**: `/generate/customer_maintenance`
- **描述**: 生成客户维护和关怀消息

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string"              // 任务ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "messages": [
    "最近工作还顺利吗？有什么需要帮助的地方随时联系我。",
    "感谢您一直以来的信任和支持，我们会继续为您提供优质服务。",
    "希望我们的产品能为您带来价值，如有任何问题请随时咨询。"
  ]
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/generate/customer_maintenance" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001"
  }'
```

### 4. 生成微信问候语

#### 请求信息
- **方法**: `POST`
- **路径**: `/generate/wechat_greeting`
- **描述**: 生成微信风格的问候语

#### 请求参数

**请求体** (JSON):
```json
{
  "tenant_id": "string",           // 租户ID，必填
  "task_id": "string",             // 任务ID，必填
  "wechat_id": "string"            // 客户微信ID，必填
}
```

#### 响应参数

**成功响应** (200):
```json
{
  "status": "success",
  "messages": [
    "👋 您好！很高兴认识您！",
    "😊 希望我们的产品能为您带来帮助！",
    "💼 专业服务，值得信赖！"
  ]
}
```

#### 示例

**请求示例**:
```bash
curl -X POST "http://localhost:8000/generate/wechat_greeting" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "task_id": "task_001",
    "wechat_id": "customer_001"
  }'
```

### 5. 服务根路径

#### 请求信息
- **方法**: `GET`
- **路径**: `/`
- **描述**: 获取服务信息和可用端点

#### 响应参数

**成功响应** (200):
```json
{
  "message": "开场白生成服务",
  "version": "1.0.0",
  "endpoints": [
    "/generate/personalized",
    "/generate/festival_greeting",
    "/generate/customer_maintenance",
    "/generate/wechat_greeting"
  ]
}
```

### 6. 健康检查

#### 请求信息
- **方法**: `GET`
- **路径**: `/health`
- **描述**: 检查服务健康状态

#### 响应参数

**成功响应** (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "service": "开场白生成服务"
}
```

## 支持的节日类型

### 中国传统节日
- 春节 (农历正月初一)
- 元宵节 (农历正月十五)
- 清明节 (公历4月5日前后)
- 端午节 (农历五月初五)
- 中秋节 (农历八月十五)
- 重阳节 (农历九月初九)

### 国际节日
- 元旦 (1月1日)
- 情人节 (2月14日)
- 妇女节 (3月8日)
- 劳动节 (5月1日)
- 儿童节 (6月1日)
- 教师节 (9月10日)
- 国庆节 (10月1日)
- 圣诞节 (12月25日)

## 个性化开场白特点

### 1. 基于客户画像
- 根据客户行业特点定制
- 考虑客户公司规模
- 结合客户历史行为

### 2. 基于产品信息
- 突出产品优势
- 强调解决方案价值
- 提供相关案例

### 3. 基于销售策略
- 不同阶段的销售话术
- 针对性的价值主张
- 个性化的服务承诺


## 最佳实践

### 1. 开场白使用建议
- **个性化开场白**: 用于初次接触客户
- **节日问候**: 在节日期间主动关怀
- **客户维护**: 定期维护客户关系
- **微信问候**: 适合微信聊天场景

### 2. 调用频率控制
- 避免频繁调用相同参数
- 建议间隔至少1分钟
