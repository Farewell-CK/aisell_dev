# 微信打招呼话术生成API

## 概述

微信打招呼话术生成API是一个基于AI的智能工具，能够根据公司信息、产品信息、微信昵称和可发送资料，自动生成专业的微信添加好友时的打招呼话术。适用于销售人员在添加客户微信时的验证消息场景。

## 功能特性

- **智能分析**: 深度分析公司资料、产品信息和客户画像
- **专业话术**: 生成符合微信验证消息场景的专业打招呼话术
- **昵称处理**: 智能判断微信昵称是否为真实姓名，合理使用
- **资料推荐**: 智能判断是否需要发送相关资料
- **长度控制**: 严格控制在30字以内，符合微信验证消息限制
- **批量生成**: 一次性生成多条话术供选择

## API接口

### 生成微信打招呼话术

**接口地址**: `POST /generate/wechat_greeting`

**请求参数**:
```json
{
    "tenant_id": "1",
    "task_id": "70",
    "wechat_id": "wxid_eh838yv64yso22"
}
```

**响应格式**:
```json
{
    "status": "success",
    "messages": [
        "您好，我是东莞一路绿灯科技的小苏，专注AI大模型应用解决方案，有需要随时联系",
        "您好，我是绿灯科技销售顾问，提供AI推理优化服务，帮您提升30%效率",
        "您好，绿灯科技专注AI应用解决方案，智能化升级有需求可详聊"
    ]
}
```

**参数说明**:
- `tenant_id`: 租户ID，必填
- `task_id`: 任务ID，必填
- `wechat_id`: 微信ID，必填

**响应字段**:
- `status`: 生成状态，"success"表示成功，"error"表示失败
- `messages`: 生成的话术列表

## 使用示例

### Python示例

```python
import requests
import json

def generate_wechat_greeting():
    url = "http://localhost:11434/generate/wechat_greeting"
    data = {
        "tenant_id": "1",
        "task_id": "70",
        "wechat_id": "wxid_eh838yv64yso22"
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    if result["status"] == "success":
        for i, message in enumerate(result["messages"], 1):
            print(f"{i}. {message}")
    else:
        print(f"生成失败: {result['messages']}")

# 调用函数
generate_wechat_greeting()
```

### cURL示例

```bash
curl -X POST "http://localhost:11434/generate/wechat_greeting" \
     -H "Content-Type: application/json" \
     -d '{
       "tenant_id": "1",
       "task_id": "70",
       "wechat_id": "wxid_eh838yv64yso22"
     }'
```

## 话术特点

### 设计原则
1. **简洁明了**: 微信验证消息字数限制，需要简洁有效
2. **价值导向**: 突出产品价值和客户收益
3. **建立信任**: 专业、真诚的沟通方式
4. **避免销售感**: 减少硬推销，增加价值分享

### 话术要求
- **长度限制**: 严格控制在30字以内
- **包含信息**: 必须包含公司或产品名称
- **昵称处理**: 根据微信昵称是否为真实姓名决定是否使用
- **语气要求**: 专业、尊重、自然
- **结尾处理**: 避免使用句号结尾，减少生硬感

## 数据来源

API会自动从数据库中获取以下信息：

1. **微信昵称**: 从`sale_wechat_account`表获取微信昵称信息
2. **公司资料**: 从`sale_knowledge`表获取公司相关信息
3. **产品资料**: 从`sale_product`表获取产品详细信息
4. **可发送资料**: 从`sale_ai_data`表获取可外发的资料清单

## 昵称处理逻辑

### 真实姓名判断
- **真实姓名**: 如"中科小苏"、"张三"、"李四"等，在打招呼中会使用
- **非真实姓名**: 如"落日余晖"、"星辰大海"等，不会在打招呼中提及

### 使用示例
- 真实姓名: "您好，我是东莞一路绿灯科技的小苏，专注AI大模型应用解决方案"
- 非真实姓名: "您好，我是东莞一路绿灯科技的销售顾问，专注AI大模型应用解决方案"

## 错误处理

### 常见错误

1. **数据库连接失败**
   ```json
   {
       "status": "error",
       "messages": ["生成微信打招呼话术失败: 数据库连接失败"]
   }
   ```

2. **参数错误**
   ```json
   {
       "status": "error", 
       "messages": ["生成微信打招呼话术失败: 缺少必要参数"]
   }
   ```

3. **AI生成失败**
   ```json
   {
       "status": "error",
       "messages": ["生成微信打招呼话术失败: AI服务异常"]
   }
   ```

## 测试

### 运行测试脚本

```bash
# 测试函数调用
python test_wechat_greeting.py

# 测试API接口
python test_api_wechat_greeting.py
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
   python start_opening_service.py
   ```

## 注意事项

1. **字数限制**: 微信验证消息有严格的字数限制，生成的话术必须控制在30字以内
2. **昵称隐私**: 确保微信昵称信息的安全性，避免泄露敏感数据
3. **数据完整性**: 确保数据库中有足够的公司信息和产品信息
4. **API限制**: 建议控制调用频率，避免过度消耗AI资源
5. **话术质量**: 生成的话术需要人工审核，确保符合公司规范

## 与其他接口的区别

| 特性 | 微信打招呼 | 客情维护 | 节日问候 |
|------|------------|----------|----------|
| 使用场景 | 添加好友验证消息 | 客户不回复后跟进 | 节日问候 |
| 字数限制 | 30字以内 | 50字以内 | 50字以内 |
| 昵称处理 | 智能判断是否使用 | 不涉及 | 不涉及 |
| 资料推荐 | 支持 | 支持 | 不支持 |

## 更新日志

- **v1.0.0**: 初始版本，支持基础微信打招呼话术生成 