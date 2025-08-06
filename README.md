# AI-Sell 智能销售助手

## 项目简介

AI-Sell 是一个基于大语言模型的智能销售助手项目，旨在打造从线索获取到客户维护的全链路AI销售解决方案。

### 项目背景
本项目是一个创业项目的核心AI对话部分开源版本，供学习交流使用。项目初衷是打造一个从找线索 → 添加客户微信 → 聊客户 → 卖产品 → 维护客户的全链路AI销售智能体。

### 项目现状
- **状态**: 开源学习版本
- **主要问题**: 
  - 模型拟人化程度不够，难以完全替代真人销售
  - 项目范围过大，缺乏明确的产品价值定位
  - 团队协作效率问题

### 未来规划
1. 欢迎其他开发者参与，共同完善项目功能
2. 探索智能硬件方向

## 项目架构

### 核心组件

#### 1. 对话引擎
- **main.py**: 多Agent协作模式（响应较慢但更智能）
  - 预处理Agent: 处理语音、图片、视频等多媒体输入
  - 团队协作Agent: 扮演销售经理角色，调度其他专业Agent
  - 专业Agent: 客户画像、产品咨询、协作处理、行为分析等
  - 聊天Agent: 负责最终的人性化输出

- **main_v2.py**: 单Agent模式（响应更快但拟人化程度较低）
  - 一个Agent通过调用多个工具完成销售任务

#### 2. API服务模块
- **description_api_serve.py**: 文件描述服务
  - 支持文本、图片、表格、PPT、文档、视频的智能描述
  - 提供文件比较和批量处理功能
  
- **opening_service.py**: 开场白生成服务
  - 个性化开场白生成
  - 节日问候语生成
  - 客户维护消息生成
  - 微信问候语生成

- **create_role_service.py**: 角色创建服务
  - 异步创建销售角色
  - 支持多种角色策略

- **wechat_style_service.py**: 微信风格服务
- **chat_test_service.py**: 聊天测试服务
- **file_reader_api.py**: 文件读取API

#### 3. 工具模块 (tools/)
- **notify.py**: 通知工具
- **database.py**: 数据库操作
- **product.py**: 产品相关工具
- **core_logic.py**: 核心逻辑
- **input_process.py**: 输入处理
- **callbacks.py**: 回调函数

#### 4. 对话代理模块 (dialog_agent/)
- **agent.py**: 代理核心逻辑
- **tools.py**: 代理工具集
- **prompts.py**: 提示词管理

## 技术栈

### 核心依赖
```python
# AI和机器学习
openai>=1.0.0
dashscope
litellm
google-adk
google-genai

# Web框架
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0

# 数据库
pymysql
sqlalchemy
pandas

# 文件处理
opencv-python
python-pptx
PyPDF2
python-docx
pdfplumber
Pillow
```

## 快速开始

### 环境准备
```bash
# 创建虚拟环境
conda create -n aisell python=3.12
conda activate aisell

# 克隆项目
git clone https://github.com/Farewell-CK/aisell_dev.git
cd aisell_dev

# 安装依赖
pip install -r requirements.txt
```

### 配置设置
1. 复制配置文件模板
```bash
cp configs/apikey.yaml.example configs/apikey.yaml
```

2. 配置API密钥
编辑 `configs/apikey.yaml`，添加您的API密钥：
```yaml
qwen:
  base_url: "your_qwen_base_url"
  api_key: "your_qwen_api_key"
ernie:
  base_url: "your_ernie_base_url" 
  api_key: "your_ernie_api_key"
```

### 启动服务

#### 启动主对话服务
```bash
# 启动多Agent协作模式（推荐用于生产环境）
uvicorn main:app --host 0.0.0.0 --port 11479 --workers 2

# 启动单Agent模式（推荐用于开发测试）
uvicorn main_v2:app --host 0.0.0.0 --port 11480 --workers 2
```

#### 启动辅助API服务
```bash
# 文件描述服务
python run_async_description_service.py

# 开场白生成服务  
python run_opening_service.py

# 角色创建服务
python run_crate_role.py

# 聊天测试服务
python run_chat_test_service.py

# 微信风格服务
python run_wechat_service.py
```

## API文档

### 主对话API

#### 处理用户输入
```http
POST /process_user_input
```

请求体:
```json
{
  "tenant_id": "租户ID",
  "task_id": "任务ID", 
  "belong_chat_id": "工作机微信ID",
  "wechat_id": "客户微信ID",
  "session_id": "会话ID",
  "user_input": [
    {
      "type": "text",
      "content": "你好",
      "timestamp": "2025-06-10 10:00:00"
    },
    {
      "type": "image", 
      "url": "图片URL",
      "timestamp": "2025-06-10 10:00:02"
    }
  ]
}
```

#### 删除会话
```http
POST /delete_session
```

### 文件描述API

#### 异步文档总结
```http
POST /api/summarize/document-async
```

#### 获取任务状态
```http
GET /api/summarize/status/{task_id}
```

### 开场白生成API

#### 生成个性化开场白
```http
POST /generate/personalized
```

#### 生成节日问候
```http
POST /generate/festival_greeting
```

### 角色创建API

#### 创建销售角色
```http
POST /create_role
```

## 项目结构

```
aisell_dev/
├── main.py                 # 多Agent协作模式主服务
├── main_v2.py             # 单Agent模式主服务
├── agents.py              # Agent定义
├── one_agents.py          # 单Agent定义
├── requirements.txt       # 项目依赖
├── configs/              # 配置文件
│   ├── apikey.yaml      # API密钥配置
│   └── database.yaml    # 数据库配置
├── api/                  # API服务模块
│   ├── description_api_serve.py  # 文件描述服务
│   ├── opening_service.py       # 开场白生成服务
│   ├── create_role_service.py   # 角色创建服务
│   └── ...
├── tools/                # 工具模块
│   ├── notify.py        # 通知工具
│   ├── database.py      # 数据库工具
│   ├── product.py       # 产品工具
│   └── ...
├── dialog_agent/         # 对话代理模块
│   ├── agent.py         # 代理核心
│   ├── tools.py         # 代理工具
│   └── prompts.py       # 提示词
├── utils/               # 工具函数
├── prompts/             # 提示词模板
├── database/            # 数据库相关
├── logs/               # 日志文件
└── tests/              # 测试文件
```

## 开发指南

### 添加新的Agent
1. 在 `agents.py` 中定义新的Agent
2. 在 `prompts/` 中添加对应的提示词
3. 在 `tools/` 中添加必要的工具函数

### 添加新的API服务
1. 在 `api/` 目录下创建新的服务文件
2. 创建对应的启动脚本 `run_*.py`
3. 更新API文档

### 数据库操作
- 使用 `tools/database.py` 进行数据库操作
- 配置文件位于 `configs/database.yaml`
- 数据库的表结构`docs/数据库迁移报告.html`

## 部署说明

### 生产环境部署
1. 使用 `main.py` 作为主服务（多Agent协作模式）
2. 配置反向代理（Nginx）
3. 使用进程管理器（如PM2）管理服务
4. 配置日志轮转和监控

### 开发环境部署
1. 使用 `main_v2.py` 作为主服务（单Agent模式）
2. 启用调试模式
3. 配置热重载

## 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 贡献流程
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目地址: https://github.com/Farewell-CK/aisell_dev
- 问题反馈: 请通过GitHub Issues提交
- Email: 3345710651@qq.com or sapder.dc@gmail.com

---

**注意**: 本项目仅供学习交流使用，微信接管、找线索等核心功能暂不公开。

            
