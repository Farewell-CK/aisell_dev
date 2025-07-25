# 客情维护话术生成API

## 概述

客情维护话术生成API是一个基于AI的智能工具，能够根据公司信息、产品信息和可发送资料，自动生成专业的微信客情维护话术。适用于客户不回复后的跟进场景。

## 功能特性

- **智能分析**: 深度分析公司资料、产品信息和客户画像
- **专业话术**: 生成符合销售场景的专业客情维护话术
- **资料推荐**: 智能判断是否需要发送相关资料
- **长度控制**: 严格控制在50字以内，确保简洁有效
- **批量生成**: 一次性生成多条话术供选择

## API接口

### 生成客情维护话术

**接口地址**: `POST /generate/customer_maintenance`

**请求参数**:
```json
{
    "tenant_id": "1",
    "task_id": "70"
}
```

**响应格式**:
```json
{
    "status": "success",
    "messages": [
        "您好，我是东莞一路绿灯科技的销售顾问，我们专注于AI大模型应用解决方案，如果您在智能化转型方面有需求，随时可以联系我",
        "您好，我们公司主要提供AI推理优化服务，能帮您提升30%的推理效率，有需要的话可以详细聊聊",
        "您好，我们专注于为企业提供AI应用解决方案，如果您对智能化升级感兴趣，我可以为您详细介绍"
    ]
}
```

**参数说明**:
- `tenant_id`: 租户ID，必填
- `task_id`: 任务ID，必填

**响应字段**:
- `status`: 生成状态，"success"表示成功，"error"表示失败
- `messages`: 生成的话术列表

## 使用示例

### Python示例

```python
import requests
import json

def generate_customer_maintenance():
    url = "http://localhost:11434/generate/customer_maintenance"
    data = {
        "tenant_id": "1",
        "task_id": "70"
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    if result["status"] == "success":
        for i, message in enumerate(result["messages"], 1):
            print(f"{i}. {message}")
    else:
        print(f"生成失败: {result['messages']}")

# 调用函数
generate_customer_maintenance()
```

### cURL示例

```bash
curl -X POST "http://localhost:11434/generate/customer_maintenance" \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_id": "1",
       "task_id": "70"
     }'
```

## 话术特点

### 设计原则
1. **价值导向**: 突出产品价值和客户收益
2. **痛点聚焦**: 针对客户可能面临的问题
3. **建立信任**: 专业、真诚的沟通方式
4. **避免销售感**: 减少硬推销，增加价值分享

### 话术要求
- **长度限制**: 严格控制在50字以内
- **包含信息**: 必须包含公司或产品名称
- **语气要求**: 专业、尊重、自然
- **结尾处理**: 避免使用句号结尾，减少生硬感

## 数据来源

API会自动从数据库中获取以下信息：

1. **公司资料**: 从`sale_knowledge`表获取公司相关信息
2. **产品资料**: 从`sale_product`表获取产品详细信息
3. **可发送资料**: 从`sale_ai_data`表获取可外发的资料清单

## 错误处理

### 常见错误

1. **数据库连接失败**
   ```json
   {
       "status": "error",
       "messages": ["生成客情维护话术失败: 数据库连接失败"]
   }
   ```

2. **参数错误**
   ```json
   {
       "status": "error", 
       "messages": ["生成客情维护话术失败: 缺少必要参数"]
   }
   ```

3. **AI生成失败**
   ```json
   {
       "status": "error",
       "messages": ["生成客情维护话术失败: AI服务异常"]
   }
   ```

## 测试

### 运行测试脚本

```bash
# 测试函数调用
python test_customer_maintenance.py

# 测试API接口
python test_api_customer_maintenance.py
```

### 健康检查

```bash
curl http://localhost:11434/health
```

## 部署说明

1. 确保数据库连接正常
2. 确保AI服务配置正确
3. 启动服务：
   ```bash
   python api/opening_service.py
   ```

## 注意事项

1. **数据完整性**: 确保数据库中有足够的公司信息和产品信息
2. **API限制**: 建议控制调用频率，避免过度消耗AI资源
3. **话术质量**: 生成的话术需要人工审核，确保符合公司规范
4. **隐私保护**: 确保客户信息的安全性，避免泄露敏感数据

## 更新日志

- **v1.0.0**: 初始版本，支持基础客情维护话术生成 