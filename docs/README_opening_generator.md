# 开场白生成器

## 项目概述

这是一个基于AI的智能开场白生成器，专门为销售团队设计。它能够根据客户信息、销售信息和不同场景自动生成个性化的聊天开场白，提高销售效率和客户响应率。

## 核心功能

### 🎯 多种开场白类型
- **个性化开场白**: 基于客户具体信息生成定制化开场白
- **行业针对性**: 针对特定行业生成专业开场白  
- **事件开场白**: 基于展会、会议等事件生成开场白
- **推荐人开场白**: 基于推荐人关系生成信任度高的开场白

### 🚀 核心特性
- **智能生成**: 基于大语言模型生成自然、专业的开场白
- **批量生成**: 一次性生成多种类型的开场白供选择
- **API服务**: 提供RESTful API接口，便于集成
- **易于使用**: 提供多种使用方式，满足不同需求

## 项目结构

```
aisell_dev/
├── utils/
│   └── opening_generator.py      # 核心开场白生成器
├── api/
│   └── opening_service.py        # FastAPI服务
├── test_opening_generator.py     # 完整测试文件
├── simple_test.py               # 简单测试文件
├── run_opening_service.py       # 服务启动脚本
├── opening_generator_usage.md   # 详细使用说明
└── README_opening_generator.md  # 本文档
```

## 快速开始

### 1. 环境准备

确保已安装必要的依赖：
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

### 3. 简单测试

运行简单测试验证功能：
```bash
python simple_test.py
```

### 4. 启动API服务

```bash
python run_opening_service.py
```

服务将在 `http://localhost:8003` 启动，您可以访问 `http://localhost:8003/docs` 查看API文档。

## 使用方式

### 方式1: 直接调用类

```python
import asyncio
from utils.opening_generator import OpeningGenerator

async def main():
    generator = OpeningGenerator()
    
    customer_info = {
        "name": "李总",
        "company": "深圳智能科技有限公司",
        "position": "技术总监",
        "industry": "人工智能",
        "city": "深圳"
    }
    
    sales_info = {
        "name": "张三",
        "company": "东莞一路绿灯科技有限公司",
        "product": "大模型应用解决方案",
        "advantage": "提升AI推理效率30%，降低GPU资源消耗50%"
    }
    
    result = await generator.generate_personalized_opening(
        customer_info, sales_info, 
        context="通过LinkedIn了解到客户在AI部署方面有丰富经验"
    )
    
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")

asyncio.run(main())
```

### 方式2: 使用便捷函数

```python
import asyncio
from utils.opening_generator import generate_opening

async def main():
    result = await generate_opening(
        "industry",
        customer_info,
        sales_info
    )
    
    if result['status'] == 'success':
        print(f"开场白: {result['opening']}")

asyncio.run(main())
```

### 方式3: API调用

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
         "advantage": "提升AI推理效率30%，降低GPU资源消耗50%"
       },
       "context": "通过LinkedIn了解到客户在AI部署方面有丰富经验"
     }'
```

## API接口

### 1. 个性化开场白
- **POST** `/generate/personalized`
- 基于客户具体信息生成定制化开场白

### 2. 行业针对性开场白
- **POST** `/generate/industry`
- 针对特定行业生成专业开场白

### 3. 事件开场白
- **POST** `/generate/event`
- 基于展会、会议等事件生成开场白

### 4. 推荐人开场白
- **POST** `/generate/referral`
- 基于推荐人关系生成信任度高的开场白

### 5. 批量生成
- **POST** `/generate/multiple`
- 一次性生成多种类型的开场白

### 6. 健康检查
- **GET** `/health`
- 服务健康状态检查

## 开场白类型详解

### 个性化开场白 (personalized)
- **适用场景**: 有客户具体信息时
- **特点**: 基于客户姓名、公司、职位等信息生成定制化开场白
- **优势**: 体现对客户的了解和重视

### 行业针对性开场白 (industry)
- **适用场景**: 针对特定行业客户
- **特点**: 突出产品在该行业的价值和适用性
- **优势**: 体现专业性和行业洞察

### 事件开场白 (event)
- **适用场景**: 基于展会、会议、活动等事件
- **特点**: 自然提及共同经历的事件
- **优势**: 建立共同话题，降低陌生感

### 推荐人开场白 (referral)
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

## 测试

### 运行完整测试
```bash
python test_opening_generator.py
```

### 运行简单测试
```bash
python simple_test.py
```

## 错误处理

### 常见问题及解决方案

1. **API密钥错误**
   - 检查 `configs/apikey.yaml` 中的API密钥配置
   - 确保API密钥有效且有足够额度

2. **网络连接问题**
   - 检查网络连接
   - 确认API服务可访问

3. **参数错误**
   - 检查输入参数格式
   - 确保必填字段不为空

## 扩展开发

如需添加新的开场白类型或修改现有逻辑：

1. 在 `OpeningGenerator` 类中添加新方法
2. 在 `api/opening_service.py` 中添加新的API端点
3. 更新提示词模板以优化生成效果

## 技术栈

- **Python 3.8+**: 主要开发语言
- **FastAPI**: Web框架
- **Pydantic**: 数据验证
- **OpenAI API**: 大语言模型接口
- **Uvicorn**: ASGI服务器

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请联系开发团队。 