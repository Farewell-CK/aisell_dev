import os
from openai import OpenAI
from tools.database import DatabaseManager
from tools.notify import send_prohibit_notify
from utils.chat import chat_qwen
from prompts.prompts import role_prompt , get_role_prompt
from utils.db_queries import select_base_info, select_talk_style, select_knowledge, select_product


async def extract_prohibit(api_key,content: str) -> list[str]:
    """
    从内容中提取禁止做的事情。
    Args:
        content: 内容

    Returns:
        list[str]: 禁止做的事情
    """
    prompt = f"""
    从禁止做的事情中提取所有禁止事项，以列表形式输出["禁止事项1", "禁止事项2", "禁止事项3", ....]
内容如下：
{content}
注意：只需要输出列表，不要输出其他内容,以json格式输出
"""
    response = await chat_qwen(api_key,prompt)
    return response

async def extract_sale_flow(api_key,content: str) -> list[str]:
    """
    从内容中提取销售流程。
    """
    prompt = f"""
    从销售流程中提取所有流程，以列表形式输出：[{{"title": "流程标题", "description": ["目标","行动","话术示例", "关键"]}}, {{"title": "流程标题", "description": ["目标","行动","话术示例", "关键"]}}, ....]
内容如下：
{content}
注意：只需要输出列表，不要输出其他内容,以json格式输出
"""
    response = await chat_qwen(api_key,prompt)
    return response

async def create_role(api_key,tenant_id,task_id):
    """
    创建角色
    Args:
        api_key: 模型API KEY
        tenant_id: 租户ID
        task_id: 任务ID

    Returns: 
        content: 角色内容, 初始的提示词
    """
    base_info = select_base_info(tenant_id,task_id)
    talk_style = select_talk_style(tenant_id,task_id)
    knowledge = select_knowledge(tenant_id,task_id)
    product = select_product(tenant_id,task_id)
    content = await chat_qwen(api_key,get_role_prompt(base_info, knowledge, product, talk_style))
    prohibit = await extract_prohibit(api_key,content)
    sale_flow = await extract_sale_flow(api_key,content)
    # 发送禁止做的事情 && 销售流程通知
    await send_prohibit_notify(tenant_id,task_id,prohibit,sale_flow)
    return content