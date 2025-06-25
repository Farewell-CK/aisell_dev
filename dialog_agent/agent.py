import os
import asyncio
import json
import requests
from contextlib import AsyncExitStack
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.runners import Runner
from google.genai import types

from .tools import speech_to_text, image_comprehension, video_comprehension, generate_customer_portrait, generate_customer_behavior, generate_product_offer, generate_base_info, generate_strategy, generate_role
from .prompts import preprocess_prompt, customer_portrait_prompt, customer_behavior_prompt, product_offer_prompt,personification_output_prompt

# 导入配置加载器
from utils.config_loader import ConfigLoader

import warnings
# 忽略所有警告
warnings.filterwarnings("ignore")

# --- 日志配置 ---
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "agent.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

print("Libraries imported.")

db_url = "sqlite:///./database/my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)
print("Session service created.")

# 初始化配置加载器
config = ConfigLoader()

# 获取环境变量
qwen_api_key = os.getenv("Qwen_API_KEY")
qwen_base_url = os.getenv("Qwen_BASE_URL")

deepseek_api_key = os.getenv("Deepseek_API_KEY")
deepseek_base_url = os.getenv("Deepseek_BASE_URL")

# 配置模型
deepseek_model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_key=config.get_api_key('deepseek'),
    api_base=config.get_api_key('deepseek', 'base_url')
)

qwen_model = LiteLlm(
    model="openai/qwen-plus-2025-04-28",  
    api_key=qwen_api_key,
    api_base=qwen_base_url
)

customer_portrait_agent = LlmAgent(
    name="customer_portrait_agent",
    model=qwen_model,
    description='使用"generate_customer_portrait"工具生成或更新客户画像。',
    instruction=customer_portrait_prompt,
    tools=[generate_customer_portrait],
)

customer_behavior_agent = LlmAgent(
    name="customer_behavior_agent",
    model=qwen_model,
    description="生成客户意图，也就是客户接下来要做的事情。",
    instruction=customer_behavior_prompt,
    tools=[generate_customer_behavior],
)

product_offer_agent = LlmAgent(
    name="product_offer_agent",
    model=qwen_model,
    description="查询相关的产品，生成产品建议，即给客户推荐什么产品。",
    instruction=product_offer_prompt,
    tools=[generate_product_offer],
)

personification_output_agent = LlmAgent(
    name="personification_output_agent",
    model=qwen_model,
    description="根据输入的指令，生成产品建议，即给客户推荐什么产品。",
    instruction=personification_output_prompt,
    tools=[],
)

# 这个为根agent，整个workflow的输入源
inputs_preprocess_agent = LlmAgent(
    name="inputs_preprocess_agent",
    model=qwen_model,
    description="根据用户输入的文本， 图片url, 音频url, 视频url等, 进行预处理并进行整理的纯文本用户输入。",
    instruction=preprocess_prompt,
    tools=[speech_to_text, image_comprehension, video_comprehension],
    output_key="text",
)

# async def create_agent():
#   """从 MCP 服务器获取工具。"""

#   tools, exit_stack = await MCPToolset.from_server(
#       connection_params=StdioServerParameters(
#           command='npx',
#           args=["-y",
#                 "@amap/amap-maps-mcp-server",
#           ],
#           # 将 API 密钥作为环境变量传递给 npx 进程
#           env={
#               "AMAP_MAPS_API_KEY": "af8a9fd3dac89fe58d1ab4a2fa142a30"
#           }
#       )
#   )

#   agent = LlmAgent(
#       model=qwen_model, # 根据需要调整
#       name='maps_assistant',
#       instruction='使用可用工具帮助用户进行地图和方向查询。',
#       tools=tools,
#   )
#   return agent, exit_stack

# root_agent = create_agent()