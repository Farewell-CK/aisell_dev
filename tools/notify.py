import requests
import json
import os 
import aiohttp
import asyncio
from datetime import datetime
from core.database_core import db_manager
from utils.logger_config import get_utils_logger
from utils.db_queries import select_wechat_name

logger = get_utils_logger()

async def send_order_notification(tenant_id,task_id,session_id,order_notification):
    """
    发送订单通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        order_notification: 订单通知
    Returns:
        response: 响应
    """
    pass

async def send_collaborate_matters(tenant_id,task_id,session_id,collaborate_matters):
    """
    发送协作事项通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        collaborate_matters: 协作事项
    Returns:
        response: 响应
    """
    pass


async def send_opening(tenant_id,task_id,session_id,opening):
    """
    发送开场白通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        opening: 开场白
    Returns:
        response: 响应
    """
    pass

async def send_customer_portrait(tenant_id,task_id,session_id,customer_portrait):
    """
    发送客户画像通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        customer_portrait: 客户画像
    Returns:
        response: 响应
    """
    url = f"{os.getenv('NOTIFY_URL')}/api/v1/notify/customer_portrait"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTIFY_API_KEY')}"
    }
    data = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "session_id": session_id,
        "customer_portrait": customer_portrait
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

async def send_customer_behavior(tenant_id,task_id,session_id,customer_behavior):
    """
    发送客户行为通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        customer_behavior: 客户行为
    Returns:
        response: 响应
    """
    url = f"{os.getenv('NOTIFY_URL')}/api/v1/notify/customer_behavior"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTIFY_API_KEY')}"
    }           
    data = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "session_id": session_id,
        "customer_behavior": customer_behavior
    }   
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

async def send_prohibit_notify(tenant_id,task_id,strategy_id,prohibit_list, sale_flow, status=2):
    """
    发送禁止做的事情 && 销售流程通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        strategy_id: 策略ID
        prohibit_list: 禁止做的事情列表
        sale_flow: 销售流程
        status: 状态 2 成功 1 失败
    Returns:
        response: 响应
    """
    for prohibit in prohibit_list:
        # 将一个单引号替换为两个单引号
        escaped_prohibit = prohibit.replace("'", "''")
        insert_query = f"""
        INSERT INTO sale_forbidden (
        strategy_id,
        text,
        tenant_id,
        create_by,
        create_time,
        is_del
    ) VALUES (
        '{strategy_id}',
        '{escaped_prohibit}',
        '{tenant_id}',
        'admin',
        NOW(),
        0
    );
        """
        db_manager.execute_insert(insert_query)
    logger.info(f"待插入销售流程: {sale_flow}")
    for i,flow in enumerate(sale_flow):
        # 将一个单引号替换为两个单引号
        escaped_title = flow['title'].replace("'", "''")
        escaped_description = str(flow['description']).replace("'", "''")
        insert_query = f"""
        INSERT INTO sale_process (
            strategy_id,
            title,
            text,
            sort,
            tenant_id,
            create_by,
            create_time,
            is_del
        ) VALUES (
            '{strategy_id}',
            '{escaped_title}',
            '{escaped_description}',
            '{i}',
            '{tenant_id}',
            'admin',
            NOW(),
            0
        );

        """
        logger.info(f"插入销售流程: {insert_query}")
        db_manager.execute_insert(insert_query)
    update_status_query = f"""
    UPDATE sale_strategy SET status = {status} WHERE id = {strategy_id} AND tenant_id = {tenant_id} AND task_id = {task_id};
    """
    db_manager.execute_update(update_status_query)
    update_reply_query = f"""
    UPDATE sale_strategy SET reply_cycle = 72, reply_times = 2 WHERE id = {strategy_id} AND tenant_id = {tenant_id} AND task_id = {task_id};
    """
    db_manager.execute_update(update_reply_query)
    return True

async def send_chat_test(tenant_id,task_id,chat_test):
    """
    发送聊天测试通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        chat_test: 聊天测试内容
    Returns:
        response: 响应
    """
    url = f"{os.getenv('NOTIFY_URL')}/api/v1/notify/chat_test"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTIFY_API_KEY')}"
    }
    data = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "chat_test": chat_test # 聊天测试内容 是一个列表
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

async def send_chat(tenant_id,task_id,session_id,wechat_id,belong_chat_id,chat_content):
    """
    发送聊天内容通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        belong_chat_id: 工作机登录的微信id
        chat_content: 聊天内容
    Returns:
        response: 响应

    chat_content : 
    {
         "content_list": [
         {
            "type": "text",
            "content": "回复内容1"
         },
         {
            "type": "file",
            "url": "需要给客户发送的文件URL"
         }
         ],
         "collaborate_list": [
         {
         "id": 1,
         "content": "协作事项内容1"
         },
         {
         "id": 2,
         "content": "协作事项内容2"
         }],
         "follow_up": {
            "is_follow_up": 1, 
            "follow_up_content": ["跟单内容1", "跟单内容2", "跟单内容3"]
         },
         "need_assistance": 1,
      }
    """
    # print(f"chat_content: {chat_content}")
    if isinstance(chat_content, str):
        collaborate_list = []
    else:
        collaborate_dic = chat_content.get("collaborate_list", [])
        wechat_name = select_wechat_name(tenant_id, wechat_id)
        collaborate_list = [collaborate['content'].replace("客户", wechat_name) for collaborate in collaborate_dic]
    for collaborate in collaborate_list:
        escaped_collaborate = collaborate.replace("'", "''")
        insert_query = f"""
        INSERT INTO sale_wechat_matter (
            content,
            belong_wechat_id,
            wechat_id,
            tenant_id,
            create_by,
            create_time,
            is_del
        ) VALUES (
            '{escaped_collaborate}',
            '{belong_chat_id}',
            '{session_id}',
            '{tenant_id}',
            'admin',
            NOW(),
            0
        );
        """
        logger.info(f"插入协作事项: {insert_query}")
        try:
            await asyncio.to_thread(db_manager.execute_insert, insert_query)
        except Exception as e:
            logger.error(f"插入协作事项失败: {e}")
    url = "http://120.77.8.73/sale/wechat/message/send"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "status": "success",
        "tenant_id": tenant_id,
        "task_id": task_id,
        "session_id": session_id,
        "belong_chat_id": belong_chat_id,
        "chat_content": chat_content # 聊天内容 是一个列表
    }
    logger.info(f"发送聊天通知: {data}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return await response.json()
    except Exception as e:
        logger.error(f"发送聊天通知失败: {e}")
        return {"status": "failed",
                "tenant_id": tenant_id,
                "task_id": task_id,
                "session_id": session_id,
                "belong_chat_id": belong_chat_id,
                "chat_content": [str(e)]
                }