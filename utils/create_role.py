import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from tools.database import DatabaseManager
from tools.notify import send_prohibit_notify
from utils.chat import chat_qwen
from prompts.prompts import role_prompt , get_role_prompt
from utils.db_queries import select_base_info, select_talk_style, select_knowledge, select_product
from utils.logger_config import get_utils_logger

# 获取工具模块的日志记录器
logger = get_utils_logger()

# 创建更大的线程池执行器，用于执行同步的数据库操作
# 增加线程池大小以支持更多并发请求
thread_pool = ThreadPoolExecutor(max_workers=50, thread_name_prefix="role_creator")

async def extract_prohibit(content: str) -> list[str]:
    """
    从内容中提取禁止做的事情。
    Args:
        content: 内容

    Returns:
        list[str]: 禁止做的事情
    """
    logger.info("开始提取禁止事项...")
    prompt = f"""
    从禁止做的事情中提取所有禁止事项，以列表形式输出["禁止事项1", "禁止事项2", "禁止事项3", ....]
内容如下：
{content}
注意：只需要输出列表，不要输出其他内容,以json格式输出
"""
    try:
        response = await chat_qwen(prompt)
        # response = json.loads(response.strip('```').strip('```json'))
        # logger.info(f"禁止事项提取完成，提取到 {len(response) if isinstance(response, list) else '未知数量'} 项")
        return response
    except Exception as e:
        logger.error(f"提取禁止事项失败: {str(e)}", exc_info=True)
        raise

async def extract_sale_flow(content: str) -> list[str]:
    """
    从内容中提取销售流程。
    """
    logger.info("开始提取销售流程...")
    prompt = f"""
    从销售流程中提取所有流程，以列表形式输出：[{{"title": "流程标题", "description": ["目标","行动","话术示例", "关键"]}}, {{"title": "流程标题", "description": ["目标","行动","话术示例", "关键"]}}, ....]
内容如下：
{content}
注意：只需要输出列表，不要输出其他内容,以json格式输出
"""
    try:
        response = await chat_qwen(prompt)
        # response = json.loads(response.strip('```').strip('```json'))
        # logger.info(f"销售流程提取完成，提取到 {len(response) if isinstance(response, list) else '未知数量'} 个流程")
        return response
    except Exception as e:
        logger.error(f"提取销售流程失败: {str(e)}", exc_info=True)
        raise

async def create_role(tenant_id, task_id, strategy_id):
    """
    创建角色
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        strategy_id: 策略ID

    Returns: 
        content: 角色内容, 初始的提示词
    """
    logger.info(f"开始创建角色 - 租户ID: {tenant_id}, 任务ID: {task_id}, 策略ID: {strategy_id}")
    
    try:
        # 并发执行所有数据库查询，而不是串行执行
        logger.info("正在并发获取所有数据...")
        
        # 创建所有数据库查询任务
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                thread_pool, select_base_info, tenant_id, task_id
            ),
            asyncio.get_event_loop().run_in_executor(
                thread_pool, select_talk_style, tenant_id, task_id
            ),
            asyncio.get_event_loop().run_in_executor(
                thread_pool, select_knowledge, tenant_id, task_id
            ),
            asyncio.get_event_loop().run_in_executor(
                thread_pool, select_product, tenant_id, task_id
            )
        ]
        
        # 等待所有数据库查询完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理查询结果
        base_info, talk_style, knowledge, product = results
        
        # 检查是否有查询异常
        if isinstance(base_info, Exception):
            logger.error(f"基础信息查询失败: {base_info}")
            base_info = []
        if isinstance(talk_style, Exception):
            logger.error(f"谈话风格查询失败: {talk_style}")
            talk_style = []
        if isinstance(knowledge, Exception):
            logger.error(f"知识库查询失败: {knowledge}")
            knowledge = []
        if isinstance(product, Exception):
            logger.error(f"产品信息查询失败: {product}")
            product = []
        
        logger.info(f"数据获取完成 - 基础信息: {len(base_info) if base_info else 0} 条, 谈话风格: {len(talk_style) if talk_style else 0} 条, 知识库: {len(knowledge) if knowledge else 0} 条, 产品: {len(product) if product else 0} 条")
        
        # 生成角色内容
        logger.info("正在生成角色内容...")
        content = await chat_qwen(get_role_prompt(base_info, knowledge, product, talk_style))
        logger.info(f"角色内容生成完成，内容长度: {len(content) if content else 0} 字符")
        
        # 并发执行禁止事项和销售流程提取
        logger.info("正在并发提取禁止事项和销售流程...")
        extract_tasks = [
            extract_prohibit(content),
            extract_sale_flow(content)
        ]
        
        prohibit, sale_flow = await asyncio.gather(*extract_tasks, return_exceptions=True)
        
        # 检查提取结果
        if isinstance(prohibit, Exception):
            logger.error(f"禁止事项提取失败: {prohibit}")
            prohibit = []
        if isinstance(sale_flow, Exception):
            logger.error(f"销售流程提取失败: {sale_flow}")
            sale_flow = []
        
        # 发送通知
        logger.info("正在发送禁止事项和销售流程通知...")
        try:
            prohibit_data = json.loads(prohibit.strip('```').strip('```json')) if isinstance(prohibit, str) else prohibit
            sale_flow_data = json.loads(sale_flow.strip('```').strip('```json')) if isinstance(sale_flow, str) else sale_flow
            logger.info(f"有{len(prohibit_data)}个禁止事项，禁止事项内容为：{prohibit_data}")
            logger.info(f"有{len(sale_flow_data)}个销售流程，销售流程内容为：{sale_flow_data}")
            await send_prohibit_notify(tenant_id, task_id, strategy_id, prohibit_data, sale_flow_data, status=2)
            logger.info("通知发送成功")
        except Exception as notify_error:
            logger.error(f"发送通知失败: {str(notify_error)}", exc_info=True)
            await send_prohibit_notify(tenant_id, task_id, strategy_id, prohibit, sale_flow, status=3)
            # 通知失败不影响角色创建流程
        
        logger.info(f"角色创建完成 - 租户ID: {tenant_id}, 任务ID: {task_id}, 策略ID: {strategy_id}")
        return content
        
    except Exception as e:
        logger.error(f"角色创建失败 - 租户ID: {tenant_id}, 任务ID: {task_id}, 策略ID: {strategy_id}, 错误: {str(e)}", exc_info=True)
        raise

async def create_role_background(tenant_id, task_id, strategy_id):
    """
    后台执行角色创建任务，不返回结果
    """
    try:
        await create_role(tenant_id, task_id, strategy_id)
        logger.info(f"后台角色创建任务完成 - 租户ID: {tenant_id}, 任务ID: {task_id}")
    except Exception as e:
        logger.error(f"后台角色创建任务失败 - 租户ID: {tenant_id}, 任务ID: {task_id}, 错误: {str(e)}", exc_info=True)