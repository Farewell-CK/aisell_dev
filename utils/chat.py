import asyncio
import os
import json
from prompts.prompts import split_sentence_prompt
from openai import OpenAI
import logging
from google.genai import types # For creating message Content/Parts

# 配置日志记录器
logger = logging.getLogger(__name__)

# @title Define Agent Interaction Function
from google.genai import types # For creating message Content/Parts

async def call_agent_async(query, runner, user_id, session_id):
    """
    Sends a query to the agent and prints the final response.
    Args:
        query: 用户输入
        runner: 智能体  // 智能体运行器
        user_id: 用户ID  //对应我们的task_id
        session_id: 会话ID  //对应我们的session_id
    Returns:
        final_response_text: 最终响应
    """
    logger.info(f"User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "智能体没有产生最终响应。" # 默认值

    # 关键概念：run_async 执行智能体逻辑并产生事件。
    # 我们遍历事件以找到最终答案。
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # 你可以取消注释下面的行以查看执行期间的*所有*事件
        # print(f"  [事件] 作者：{event.author}，类型：{type(event).__name__}，最终：{event.is_final_response()}，内容：{event.content}")

        # 关键概念：is_final_response() 标记轮次的结束消息。
        if event.is_final_response():
            if event.content and event.content.parts:
                # 假设第一部分中的文本响应
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # 处理潜在错误/升级
                final_response_text = f"智能体升级：{event.error_message or '无特定消息。'}"
                # 如果需要，在这里添加更多检查（例如，特定错误代码）
            break # 找到最终响应后停止处理事件
    logger.info(f"Agent Response: {final_response_text}")
    return final_response_text


async def chat_qwen(api_key : str, prompt : str) -> str:
    """
    调用qwen模型
    Args:
        api_key: 模型API KEY
        prompt: 提示词
    Returns:
        response: 响应
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


async def chat_test(api_key : str, system_prompt : str, query : str) -> str:
    """
    调用qwen模型进行测试
    Args:
        api_key: 模型API KEY
        system_prompt: 系统提示词
        query: 用户输入
    Returns:
        response: 响应
    """
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ) 
    completion = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
    )
    return completion.choices[0].message.content

async def split_sentence(api_key : str, sentence : str) -> list[str]:
    """
    切分句子
    Args:
        api_key: 模型API KEY
        sentence: 句子
    Returns:
        response: 响应
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[
            {"role": "system", "content": split_sentence_prompt},
            {"role": "user", "content": sentence}
        ],
    )
    return json.loads(completion.choices[0].message.content.strip('```').strip('json'))