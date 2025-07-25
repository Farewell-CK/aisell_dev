import os
import requests
import json
from core.database_core import db_manager
from prompts.prompts import select_ai_data

def generate_customer_portrait(user_input: str) -> dict:
    """根据历史聊天记录和用户发送的最新信息 生成或更新 用户画像。

    Args:
        user_input (str): 用户输入的文本。

    Returns:
        dict: 包含用户画像的字典。
    """
    # 这里可以添加生成用户画像的逻辑
    # 例如，调用模型生成用户画像
    return {
        "status": "success",
        "customer_portrait": f"用户画像: {user_input}"
    }

def generate_customer_behavior(user_input: str) -> dict:
    """根据用户输入以及历史聊天记录生成客户意图。

    Args:
        user_input (str): 用户输入的文本。

    Returns:
        dict: 包含客户意图的字典。
    """
    # 这里可以添加生成客户意图的逻辑
    # 例如，调用模型生成客户意图
    return {
        "status": "success",
        "customer_intent": f"客户意图: {user_input}"
    }

def generate_product_offer(user_input: str) -> dict:
    """查询产品价格信息，并根据用户的生成产品建议。

    Args:
        user_input (str): 用户输入的文本。

    Returns:
        dict: 包含产品建议的字典。
    """
    # 这里可以添加生成产品建议的逻辑
    # 例如，调用模型生成产品建议
    return {
        "status": "success",
        "product_offer": f"产品建议: {user_input}"
    }

def get_weather_from_amap(city: str) -> dict:
    """
    调用高德地图API获取指定城市的天气信息。

    Args:
        city (str): 需要查询天气的城市名称或城市编码。

    Returns:
        dict: 包含查询状态和天气信息的字典，如果请求失败则status为"error"。
    """
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "city": city,
        "key": os.getenv("Gaode_map_API_KEY"),  # 使用环境变量或传入的Key
        "extensions": "all",  # 基础天气信息
        "output": "json"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 检查请求是否成功

        weather_data = response.json()
        if weather_data.get("status") == "1":
            return {"status": "success", "weather": weather_data["lives"]}
            # return weather_data
        else:
            print(f"查询失败: {weather_data.get('info')}")
            # return None
            return {"status": "error", "message":f"查询失败: {weather_data.get('info')}"}

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        # return None
        return {"status": "error", "message":f"网络请求错误: {e}"}
    except json.JSONDecodeError as e:
        print(f"JSON解码错误: {e}")
        # return None
        return {"status": "error", "message":f"JSON解码错误: {e}"}    

def update_customer_portrait(customer_portrait: dict) -> dict:
    """
    更新客户画像。
    
    Args:
        customer_portrait (dict): {
            "name": "客户姓名",
            "phone": "客户手机号",
            "industry": "客户行业",
            "department": "客户部门",
            "company": "客户公司",
            "position": "客户职位",
            "company_size": "客户公司规模",
            "city": "客户城市"
        }

    Returns:
        {
            "status": "更新状态，     #success表示更新成功，error表示更新失败",
            "customer_portrait": "客户画像"
        }
    """
    try:
    
        pass # 发送通知，更新客户画像

        return {
            "status": "success",
            "customer_portrait": f"用户画像: {customer_portrait}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"更新客户画像失败: {str(e)}"
        }


def update_customer_behavior(customer_behavior: str) -> dict:
    """
    更新客户意图。
    
    Args:
        customer_behavior: "客户行为"

    Returns:
        {
            "status": "success",
            "customer_behavior": "客户意图"
        }
    """
    try:

        pass # 发送通知，更新客户行为

        return {
            "status": "success",
            "customer_behavior": f"客户意图: {customer_behavior}"
        }
    except Exception as e:  
        return {
            "status": "error",
            "message": f"更新客户意图失败: {str(e)}"
        }


def collaborate_matters(collaborate_matters_type: str, task_id: int, tenant_id: int, ) -> dict:
    """
    执行相关协作事项。
    
    Args:
        collaborate_matters_type: "协作事项类型"
        task_id: "任务ID"
        tenant_id: "租户ID"
    Returns:
        {
            "status": "success",
            "message": "执行协作事项成功"
        }
    """
    try:
        pass # 执行相关协作事项
    except Exception as e:
        return {
            "status": "error",
            "message": f"执行协作事项失败: {str(e)}"
        }

## 暂时不使用跟单事项通知了，使用chat_agent中判断是否需要跟单
def follow_up_notification(tenant_id: int, task_id: int, session_id: str, content: str):
    """
    发送跟单通知。
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        session_id: 会话ID
        content: 跟单内容, 客户在一段时间后没有回复，跟单时需要发送的内容
    Returns:
        {
            "status": "success",
            "message": "发送跟单通知成功"
        }
    """
    pass

def select_file(tenant_id: int, task_id: int) -> dict:
    """
    查询相关文件的内容和url。
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
    Returns:
        {
            "status": "success",
            "message": "查询文件成功",
            "file_list": [
                {
                    "file_description": "文件描述",
                    "file_url": "文件url"
                }
            ]
        }
    """
    try:
        ai_data = select_ai_data(tenant_id, task_id)
        file_list = []
        for data in ai_data:
            file_list.append({
                "file_description": data["ai_text"],
                "file_url": data["url"]
            })
        return {
            "status": "success",
            "message": "查询文件成功",
            "file_list": file_list
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"没有相关文件或者查询文件失败: {str(e)}"
        }
