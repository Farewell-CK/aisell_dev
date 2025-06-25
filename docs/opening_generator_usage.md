# 开场白生成器使用说明

## 概述

开场白生成器是一个基于AI的智能工具，能够根据客户信息、销售信息和场景自动生成个性化的聊天开场白。支持多种开场白类型，适用于不同的销售场景。

## 功能特性

- **个性化开场白**: 基于客户具体信息生成定制化开场白
- **行业针对性**: 针对特定行业生成专业开场白
- **事件开场白**: 基于展会、会议等事件生成开场白
- **推荐人开场白**: 基于推荐人关系生成信任度高的开场白
- **批量生成**: 一次性生成多种类型的开场白供选择

## 安装和配置

### 1. 环境要求

确保已安装以下依赖：
```bash
pip install fastapi uvicorn pydantic openai
```

### 2. 配置API密钥

在 `configs/apikey.yaml` 中配置您的API密钥：
```yaml
api_keys:
  qwen:
    api_key: "your_qwen_api_key_here"
```

## 使用方法

### 方法1: 直接调用类

```python
import asyncio
from utils.opening_generator import OpeningGenerator

async def main():
    # 初始化生成器
    generator = OpeningGenerator()
    
    # 客户信息
    customer_info = {
        "name": "李总",
        "company": "深圳智能科技有限公司",
        "position": "技术总监",
        "industry": "人工智能",
        "city": "深圳"
    }
    
    # 销售信息
    sales_info = {
        "name": "张三",
        "company": "东莞一路绿灯科技有限公司",
        "product": "大模型应用解决方案",
        "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
        "scenarios": "智能制造、金融风控、医疗诊断"
    }
    
    # 生成个性化开场白
    result = await generator.generate_personalized_opening(
        customer_info, 
        sales_info, 
        context="通过LinkedIn了解到客户在AI部署方面有丰富经验"
    )
    
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")
    else:
        print(f"错误: {result['message']}")

# 运行
asyncio.run(main())
```

### 方法2: 使用便捷函数

```python
import asyncio
from utils.opening_generator import generate_opening

async def main():
    customer_info = {
        "name": "陈总",
        "company": "东莞精密制造有限公司",
        "position": "生产总监",
        "industry": "制造业",
        "city": "东莞"
    }
    
    sales_info = {
        "name": "李四",
        "company": "东莞一路绿灯科技有限公司",
        "product": "智能质检解决方案",
        "advantage": "提升质检准确率95%，降低人工成本60%",
        "scenarios": "汽车零部件、电子产品、医疗器械"
    }
    
    # 生成行业针对性开场白
    result = await generate_opening(
        "industry",
        customer_info,
        sales_info
    )
    
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")

asyncio.run(main())
```

### 方法3: 通过API服务

#### 启动服务
```bash
python run_opening_service.py
```

#### API调用示例

**1. 生成个性化开场白**
```bash
curl -X POST "http://localhost:8003/generate/personalized" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_info": {
         "name": "李总",
         "company": "深圳智能科技有限公司",
         "position": "技术总监",
         "industry": "人工智能",
         "city": "深圳"
       },
       "sales_info": {
         "name": "张三",
         "company": "东莞一路绿灯科技有限公司",
         "product": "大模型应用解决方案",
         "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
         "scenarios": "智能制造、金融风控、医疗诊断"
       },
       "context": "通过LinkedIn了解到客户在AI部署方面有丰富经验"
     }'
```

**2. 生成行业针对性开场白**
```bash
curl -X POST "http://localhost:8003/generate/industry" \
     -H "Content-Type: application/json" \
     -d '{
       "industry": "制造业",
       "customer_info": {
         "name": "陈总",
         "company": "东莞精密制造有限公司",
         "position": "生产总监",
         "industry": "制造业",
         "city": "东莞"
       },
       "sales_info": {
         "name": "李四",
         "company": "东莞一路绿灯科技有限公司",
         "product": "智能质检解决方案",
         "advantage": "提升质检准确率95%，降低人工成本60%",
         "scenarios": "汽车零部件、电子产品、医疗器械"
       }
     }'
```

**3. 生成事件开场白**
```bash
curl -X POST "http://localhost:8003/generate/event" \
     -H "Content-Type: application/json" \
     -d '{
       "event_type": "展会",
       "event_info": {
         "event_name": "2024深圳AI技术峰会",
         "event_time": "上周",
         "event_location": "深圳会展中心"
       },
       "customer_info": {
         "name": "王总",
         "company": "深圳科技公司",
         "position": "CEO",
         "industry": "人工智能",
         "city": "深圳"
       },
       "sales_info": {
         "name": "张三",
         "company": "东莞一路绿灯科技有限公司",
         "product": "大模型应用解决方案",
         "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
         "scenarios": "智能制造、金融风控、医疗诊断"
       }
     }'
```

**4. 生成推荐人开场白**
```bash
curl -X POST "http://localhost:8003/generate/referral" \
     -H "Content-Type: application/json" \
     -d '{
       "referrer_info": {
         "name": "王经理",
         "relationship": "合作伙伴"
       },
       "customer_info": {
         "name": "李总",
         "company": "深圳智能科技有限公司",
         "position": "技术总监",
         "industry": "人工智能",
         "city": "深圳"
       },
       "sales_info": {
         "name": "张三",
         "company": "东莞一路绿灯科技有限公司",
         "product": "大模型应用解决方案",
         "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
         "scenarios": "智能制造、金融风控、医疗诊断"
       }
     }'
```

**5. 批量生成多种开场白**
```bash
curl -X POST "http://localhost:8003/generate/multiple" \
     -H "Content-Type: application/json" \
     -d '{
       "customer_info": {
         "name": "李总",
         "company": "深圳智能科技有限公司",
         "position": "技术总监",
         "industry": "人工智能",
         "city": "深圳"
       },
       "sales_info": {
         "name": "张三",
         "company": "东莞一路绿灯科技有限公司",
         "product": "大模型应用解决方案",
         "advantage": "提升AI推理效率30%，降低GPU资源消耗50%",
         "scenarios": "智能制造、金融风控、医疗诊断"
       },
       "opening_types": ["personalized", "industry"],
       "context": "通过LinkedIn了解到客户在AI部署方面有丰富经验"
     }'
```

## 开场白类型说明

### 1. 个性化开场白 (personalized)
- **适用场景**: 有客户具体信息时
- **特点**: 基于客户姓名、公司、职位等信息生成定制化开场白
- **优势**: 体现对客户的了解和重视

### 2. 行业针对性开场白 (industry)
- **适用场景**: 针对特定行业客户
- **特点**: 突出产品在该行业的价值和适用性
- **优势**: 体现专业性和行业洞察

### 3. 事件开场白 (event)
- **适用场景**: 基于展会、会议、活动等事件
- **特点**: 自然提及共同经历的事件
- **优势**: 建立共同话题，降低陌生感

### 4. 推荐人开场白 (referral)
- **适用场景**: 通过推荐人介绍
- **特点**: 提及推荐人，建立信任基础
- **优势**: 提高客户接受度和信任度

## 最佳实践

### 1. 信息准备
- 收集尽可能详细的客户信息
- 准备清晰的产品价值主张
- 了解客户所在行业的特点

### 2. 场景选择
- 根据客户来源选择合适的开场白类型
- 展会客户优先使用事件开场白
- 推荐客户优先使用推荐人开场白

### 3. 个性化调整
- 生成的开场白可以根据具体情况进行微调
- 保持自然、真诚的语气
- 避免过度推销

### 4. 效果评估
- 记录不同开场白的客户响应率
- 根据反馈调整开场白策略
- 持续优化生成参数

## 错误处理

### 常见错误及解决方案

1. **API密钥错误**
   - 检查 `configs/apikey.yaml` 中的API密钥配置
   - 确保API密钥有效且有足够额度

2. **网络连接问题**
   - 检查网络连接
   - 确认API服务可访问

3. **参数错误**
   - 检查输入参数格式
   - 确保必填字段不为空

## 测试

运行测试文件验证功能：
```bash
python test_opening_generator.py
```

## 扩展开发

如需添加新的开场白类型或修改现有逻辑，可以：

1. 在 `OpeningGenerator` 类中添加新方法
2. 在 `api/opening_service.py` 中添加新的API端点
3. 更新提示词模板以优化生成效果

## 技术支持

如有问题或建议，请联系开发团队。 