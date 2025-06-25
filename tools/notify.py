import requests
import json
import os 

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

async def send_prohibit_notify(tenant_id,task_id,prohibit_list, sale_flow):
    """
    发送禁止做的事情 && 销售流程通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        prohibit_list: 禁止做的事情列表
        sale_flow: 销售流程
    Returns:
        response: 响应
    """
    url = f"{os.getenv('NOTIFY_URL')}/api/v1/notify/prohibit"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTIFY_API_KEY')}"
    }
    data = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "prohibit_list": prohibit_list,
        "sale_flow": sale_flow
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

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

async def send_chat(tenant_id,task_id,session_id,chat_content):
    """
    发送聊天内容通知
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        chat_content: 聊天内容 是一个列表
    Returns:
        response: 响应
    """
    url = f"{os.getenv('NOTIFY_URL')}/api/v1/notify/chat"
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTIFY_API_KEY')}"
    }
    data = {
        "tenant_id": tenant_id,
        "task_id": task_id,
        "session_id": session_id,
        "chat_content": chat_content # 聊天内容 是一个列表
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()