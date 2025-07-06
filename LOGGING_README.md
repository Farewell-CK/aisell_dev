# 统一日志配置说明

## 概述

本项目已实现统一的日志配置系统，确保所有模块的日志输出格式一致，便于调试和监控。

## 日志配置特性

### 1. 统一的日志格式
- **时间戳**: `YYYY-MM-DD HH:MM:SS`
- **模块名**: 标识日志来源模块
- **日志级别**: INFO, WARNING, ERROR, DEBUG
- **函数名和行号**: 便于定位代码位置
- **消息内容**: 具体的日志信息

### 2. 多输出目标
- **控制台输出**: 实时查看日志
- **应用日志文件**: `logs/app_YYYY-MM-DD.log` (包含所有级别日志)
- **错误日志文件**: `logs/error_YYYY-MM-DD.log` (仅包含ERROR级别日志)

### 3. 日志轮转
- 单个日志文件最大10MB
- 保留最近30个日志文件
- 按日期自动创建新文件

## 使用方法

### 1. 导入日志配置
```python
from utils.logger_config import get_api_logger, get_summarizer_logger, get_database_logger, get_utils_logger
```

### 2. 获取对应的日志记录器
```python
# API服务日志
api_logger = get_api_logger()

# 文档总结器日志
summarizer_logger = get_summarizer_logger()

# 数据库操作日志
db_logger = get_database_logger()

# 工具模块日志
utils_logger = get_utils_logger()
```

### 3. 使用日志记录器
```python
# 信息级别
logger.info("这是一条信息日志")

# 警告级别
logger.warning("这是一条警告日志")

# 错误级别（包含堆栈跟踪）
logger.error("这是一条错误日志", exc_info=True)

# 调试级别
logger.debug("这是一条调试日志")
```

## 已修改的文件

### 1. 新增文件
- `utils/logger_config.py`: 统一的日志配置模块

### 2. 修改的文件
- `run_async_description_service.py`: 使用统一日志配置
- `api/description_api_serve.py`: 将print替换为日志输出
- `utils/file_description.py`: 使用统一日志配置
- `utils/db_insert.py`: 将print替换为日志输出
- `run_crate_role.py`: 使用统一日志配置
- `api/create_role_service.py`: 使用统一日志配置，添加请求ID追踪
- `utils/create_role.py`: 添加详细的业务日志记录

## 日志示例

### 控制台输出
```
2025-07-05 15:22:01 - api - INFO - test_logging:20 - API服务日志测试 - 信息级别
2025-07-05 15:22:01 - api - WARNING - test_logging:21 - API服务日志测试 - 警告级别
2025-07-05 15:22:01 - api - ERROR - test_logging:22 - API服务日志测试 - 错误级别
```

### 日志文件结构
```
logs/
├── app_2025-07-05.log      # 应用日志（所有级别）
├── error_2025-07-05.log    # 错误日志（仅ERROR级别）
└── ...
```

## 测试日志配置

运行测试脚本验证日志配置：
```bash
# 测试基础日志配置
python test_logging.py

# 测试角色创建服务日志配置
python test_role_service_logging.py
```

## 注意事项

1. **日志级别**:
   - DEBUG: 调试信息
   - INFO: 一般信息
   - WARNING: 警告信息
   - ERROR: 错误信息

2. **错误日志**: 使用 `logger.error(message, exc_info=True)` 可以记录完整的堆栈跟踪

3. **性能考虑**: 日志文件会自动轮转，避免单个文件过大

4. **编码**: 所有日志文件使用UTF-8编码，支持中文输出

## 迁移指南

如果要将其他模块的print语句替换为日志输出：

1. 导入对应的日志记录器
2. 将 `print(message)` 替换为 `logger.info(message)`
3. 将错误处理中的print替换为 `logger.error(message, exc_info=True)`

### 角色创建服务日志配置示例

```python
# 在API服务中
from utils.logger_config import get_api_logger
logger = get_api_logger()

# 添加请求ID追踪
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"收到请求: {request.method} {request.url.path}, 请求ID: {request_id}")
    response = await call_next(request)
    logger.info(f"请求处理完成: {request.method} {request.url.path}, 请求ID: {request_id}, 状态码: {response.status_code}")
    return response

# 在业务逻辑中
from utils.logger_config import get_utils_logger
logger = get_utils_logger()

logger.info(f"开始创建角色 - 租户ID: {tenant_id}, 任务ID: {task_id}")
logger.info("正在获取基础信息...")
logger.error(f"角色创建失败: {str(e)}", exc_info=True)
```

## 配置自定义

如需修改日志配置，可以编辑 `utils/logger_config.py` 文件：

- 修改日志格式
- 调整日志级别
- 更改文件大小限制
- 自定义日志文件路径 