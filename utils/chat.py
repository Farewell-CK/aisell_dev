import time
import json
from openai import OpenAI
import logging
from google.genai import types # For creating message Content/Parts
from google.adk.runners import Runner # 导入 Runner 用于类型提示
from google.adk.events import Event, EventActions
from utils.config_loader import ConfigLoader

from typing import Dict, Any # 用于 Dict 和 Any 类型提示

# 配置日志记录器
logger = logging.getLogger(__name__)

# @title Define Agent Interaction Function
from google.genai import types # For creating message Content/Parts

config = ConfigLoader()

async def call_agent_async_v2(query: str, runner: Runner, user_id: str, session_id: str, request_body: dict) -> str:
    """
    向智能体发送查询并打印最终响应。
    Args:
        query: 用户输入
        runner: 智能体运行器实例
        user_id: 用户ID //对应我们的task_id
        session_id: 会话ID //对应我们的session_id
        request_body: 整个请求体，将被存储到session.state
    Returns:
        final_response_text: 最终响应
    """
    logger.info(f"User Query: {query}")

    # 以 ADK 格式准备用户消息
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "智能体没有产生最终响应。" # 默认值

    # 关键概念：run_async 执行智能体逻辑并产生事件。
    # 我们遍历事件以找到最终答案。
    # 将 request_body 存储到 additional_state 中，使其可在 Agent 的 session.state 中访问
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
        additional_state={"request_data": request_body} # 将整个请求体存储在 'request_data' 键下
    ):
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
async def call_agent_async_v1(query, runner, user_id, session_id):
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

async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str, request_body: Dict[str, Any]) -> str:
    """
    向智能体发送查询并打印最终响应。
    Args:
        query: 用户输入
        runner: 智能体运行器实例
        user_id: 用户ID //对应我们的task_id
        session_id: 会话ID //对应我们的session_id
        request_body: 整个请求体，将被存储到session.state
    Returns:
        final_response_text: 最终响应
    """
    logger.info(f"User Query: {query}")

    # 1. 尝试获取现有会话
    session = await runner.session_service.get_session(
        app_name=runner.app_name, # Runner 实例在 main.py 中已设置 app_name
        user_id=user_id,
        session_id=session_id+user_id
    )

    # 2. 根据会话是否存在来初始化或更新其状态
    if not session:
        # 如果会话不存在 (第一次请求)，创建新会话并用 request_body 初始化其状态
        logger.info(f"创建新会话: {session_id} for user: {user_id}")
        session = await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id+user_id,
            state={"request_data": request_body} # 将 request_body 存储在 'request_data' 键下
        )
    else:
        # 如果会话已存在，创建一个系统事件来更新会话状态
        # 使用 state_delta 可以确保新的或更新的字段被合并到现有状态中
        logger.info(f"更新现有会话: {session_id} 的状态。")
        current_time = time.time() # 获取当前时间戳用于事件
        state_update_event = Event(
            invocation_id=f"inv_{session_id+user_id}_{int(current_time)}", # 生成一个唯一的调用 ID
            author="system", # 表明这是一个系统级的状态更新事件
            actions=EventActions(state_delta={"request_data": request_body}), # 将 request_body 存储在 'request_data' 键下
            timestamp=current_time
        )
        await runner.session_service.append_event(session, state_update_event)

    # 3. 准备用户消息
    content = types.Content(role='user', parts=[types.Part(text=str(query))])

    final_response_text = "智能体没有产生最终响应。" # 默认值
    last_response_text = final_response_text

    # 4. 运行 Agent。此时，会话状态（以及 Agent 的 invocation_context.state）
    # 应该已经包含了 request_body 中的所有字段。
    # 由于我们在此处手动管理了会话状态的更新，Runner.run_async 不再需要额外的 state 参数。
    print(f"content的类型: {type(content)}")
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id+user_id,
        new_message=content,
    ):
        # 记录所有事件，帮助调试
        logger.info(f"事件: 作者={event.author}, 类型={type(event).__name__}, 最终={event.is_final_response()}")
        
        if event.content and event.content.parts:
            current_response = event.content.parts[0].text
            logger.info(f"当前响应: {current_response}")
            
            # 更新最后的响应
            last_response_text = current_response
            
            # 如果是最终响应，更新final_response_text
            if event.is_final_response():
                final_response_text = current_response
                logger.info(f"找到最终响应: {final_response_text}")
        
        elif event.actions and event.actions.escalate:
            final_response_text = f"智能体升级：{event.error_message or '无特定消息。'}"
            logger.info(f"智能体升级: {final_response_text}")
            break
    
    # 如果没有找到明确的最终响应，使用最后一个响应
    if final_response_text == "智能体没有产生最终响应。" and last_response_text != final_response_text:
        final_response_text = last_response_text
        logger.info(f"使用最后一个响应作为最终响应: {final_response_text}")
    
    logger.info(f"Agent Response: {final_response_text}")
    return final_response_text

async def chat_qwen(prompt : str) -> str:
    """
    调用qwen模型
    Args:
        api_key: 模型API KEY
        prompt: 提示词
    Returns:
        response: 响应
    """
    api_key = config.get_api_key('qwen', 'api_key')
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content


async def chat_test(api_key : str, query : list[dict]) -> tuple[str, dict]:
    """
    调用qwen模型进行测试
    Args:
        api_key: 模型API KEY
        query: 用户输入
    Returns:
        response: 响应
    """
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ) 
    completion = client.chat.completions.create(
        model="qwen-vl-max-latest",
        messages=query
    )
    return completion.choices[0].message.content, completion.choices[0].message.model_dump()

async def split_sentence(api_key : str, sentence : str) -> list[str]:
    """
    切分句子
    Args:
        api_key: 模型API KEY
        sentence: 句子
    Returns:
        response: 响应
    """
    # 延迟导入以避免循环导入
    from prompts.prompts import split_sentence_prompt
    
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

class GenerateSalesProcess:
    def __init__(self, api_key : str, model : str):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def generate_sales_process(self, company_info : str, product_info : str) -> str:
        """
        生成销售流程
        Args:
            api_key: 模型API KEY
            process_data: 销售流程数据
        Returns:
            response: 响应
        """
        prompt = f"""
        你正在为一个销售人员生成一个销售流程，请根据以下数据生成一个销售流程：
        销售人员公司信息：
        {company_info}
        销售产品信息：
        {product_info}

        请注意，销售流程必须符合以下要求：
        1. 销售流程必须符合销售流程的规范
        2. 销售流程必须符合销售流程的规范
        3. 销售流程必须符合销售流程的规范
        4. 销售流程必须符合销售流程的规范
        """
        

    def generate_forbidden_content(self, process_data : list[dict]) -> str:
        """
        生成禁忌内容
        Args:
            api_key: 模型API KEY
            process_data: 销售流程数据
        Returns:
            response: 响应
        """
    