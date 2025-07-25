# 开场白生成服务概览

## 服务简介

开场白生成服务是一个基于AI的智能工具，为销售团队提供多种场景下的专业话术生成服务。该服务集成了公司信息、产品信息和客户画像分析，能够生成个性化、专业化的销售话术。

## 服务地址

- **服务地址**: http://localhost:11434
- **API文档**: http://localhost:11434/docs
- **健康检查**: http://localhost:11434/health

## 可用接口

### 1. 个性化开场白生成
- **接口**: `POST /generate/personalized`
- **用途**: 生成日常聊天中的个性化开场白
- **字数限制**: 15字以内
- **特色**: 支持微信昵称智能处理，可发送资料推荐

### 2. 节日问候语生成
- **接口**: `POST /generate/festival_greeting`
- **用途**: 生成节日或日常问候语
- **字数限制**: 50字以内
- **特色**: 支持公历和农历节日识别，自动生成相应问候语

### 3. 客情维护话术生成
- **接口**: `POST /generate/customer_maintenance`
- **用途**: 生成客户不回复后的跟进话术
- **字数限制**: 50字以内
- **特色**: 针对客户不回复场景优化，支持资料推荐

### 4. 微信打招呼话术生成
- **接口**: `POST /generate/wechat_greeting`
- **用途**: 生成微信添加好友时的验证消息
- **字数限制**: 30字以内
- **特色**: 专门针对微信验证消息场景，智能昵称处理

## 接口对比表

| 特性 | 个性化开场白 | 节日问候 | 客情维护 | 微信打招呼 |
|------|--------------|----------|----------|------------|
| **使用场景** | 日常聊天开场 | 节日问候 | 客户不回复后跟进 | 添加好友验证消息 |
| **字数限制** | 15字以内 | 50字以内 | 50字以内 | 30字以内 |
| **昵称处理** | ✅ 智能判断 | ❌ 不涉及 | ❌ 不涉及 | ✅ 智能判断 |
| **资料推荐** | ✅ 支持 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| **节日识别** | ❌ 不支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| **数据来源** | 3个表 | 1个表 | 3个表 | 4个表 |

## 数据来源

所有接口都会自动从数据库中获取相关信息：

### 基础数据表
- **`sale_knowledge`**: 公司资料和知识库信息
- **`sale_product`**: 产品详细信息
- **`sale_ai_data`**: 可发送给客户的资料清单
- **`sale_wechat_account`**: 微信账号和昵称信息

### 数据获取逻辑
1. **公司信息**: 根据租户ID和任务ID获取相关公司资料
2. **产品信息**: 根据租户ID和任务ID获取相关产品信息
3. **可发送资料**: 根据租户ID和任务ID获取可外发的资料
4. **微信昵称**: 根据租户ID和微信ID获取微信昵称

## 技术架构

### AI模型
- **主要模型**: 文心一言 (ernie-4.5-turbo-128k)
- **备用模型**: 通义千问 (qwen-plus-latest)
- **调用方式**: 异步调用，支持并发处理

### 数据库
- **类型**: MySQL
- **连接池**: 支持连接池管理
- **查询优化**: 使用索引优化查询性能

### 错误处理
- **异常捕获**: 完善的异常处理机制
- **日志记录**: 详细的日志记录，便于调试
- **错误返回**: 统一的错误信息格式

## 使用示例

### 启动服务
```bash
python start_opening_service.py
```

### 测试所有接口
```bash
# 测试个性化开场白
python test_opening_generator.py

# 测试节日问候
python test_festival_greeting.py

# 测试客情维护
python test_customer_maintenance.py

# 测试微信打招呼
python test_wechat_greeting.py
```

### API调用示例
```bash
# 个性化开场白
curl -X POST "http://localhost:11434/generate/personalized" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "1", "task_id": "70", "wechat_id": "wxid_eh838yv64yso22"}'

# 节日问候
curl -X POST "http://localhost:11434/generate/festival_greeting" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "1", "task_id": "70", "wechat_id": "wxid_eh838yv64yso22", "date": "2024-06-10"}'

# 客情维护
curl -X POST "http://localhost:11434/generate/customer_maintenance" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "1", "task_id": "70"}'

# 微信打招呼
curl -X POST "http://localhost:11434/generate/wechat_greeting" \
     -H "Content-Type: application/json" \
     -d '{"tenant_id": "1", "task_id": "70", "wechat_id": "wxid_eh838yv64yso22"}'
```

## 配置要求

### 环境变量
```bash
# 文心一言配置
ERNIE_API_KEY=your_ernie_api_key
ERNIE_BASE_URL=https://qianfan.baidubce.com/v2

# 通义千问配置
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 数据库配置
```yaml
# configs/database.yaml
database:
  host: localhost
  port: 3306
  username: root
  password: your_password
  database: sale
```

## 监控和维护

### 健康检查
```bash
curl http://localhost:11434/health
```

### 日志查看
```bash
# 查看服务日志
tail -f logs/opening_service.log

# 查看错误日志
grep "ERROR" logs/opening_service.log
```

### 性能监控
- **响应时间**: 平均响应时间 < 3秒
- **并发处理**: 支持多并发请求
- **错误率**: 错误率 < 1%

## 最佳实践

### 1. 数据准备
- 确保数据库中有完整的公司信息
- 确保产品信息准确且详细
- 定期更新可发送的资料清单

### 2. 话术优化
- 定期分析生成话术的效果
- 根据客户反馈调整提示词
- 进行A/B测试优化话术质量

### 3. 系统维护
- 定期检查数据库连接状态
- 监控AI服务的可用性
- 及时更新依赖包和配置

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确认数据库服务状态
   - 检查网络连接

2. **AI服务调用失败**
   - 检查API密钥配置
   - 确认API服务可用性
   - 检查网络连接

3. **话术生成质量差**
   - 检查数据库中的信息完整性
   - 优化提示词模板
   - 调整生成参数

### 联系支持
如遇到问题，请查看日志文件或联系技术支持团队。 