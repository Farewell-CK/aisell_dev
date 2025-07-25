import datetime
import random
from typing import List, Tuple, Optional
import lunarcalendar
from lunarcalendar import Converter, Solar, Lunar
from utils.chat import chat_qwen

# 公历节日
SOLAR_FESTIVALS = {
    "01-01": "元旦",
    "02-14": "情人节",
    "03-08": "妇女节",
    "05-01": "劳动节",
    "06-01": "儿童节",
    "10-01": "国庆节",
    "12-25": "圣诞节",
}
# 农历节日
LUNAR_FESTIVALS = {
    "01-01": "春节",
    "05-05": "端午节",
    "08-15": "中秋节",
}

def get_festival_by_date(date_str: str) -> Tuple[Optional[str], str]:
    """
    根据日期字符串判断节日，支持公历和农历
    :param date_str: "2024-06-10"
    :return: (节日名, key)
    """
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        # 先查公历节日
        solar_key = date.strftime("%m-%d")
        if solar_key in SOLAR_FESTIVALS:
            return SOLAR_FESTIVALS[solar_key], solar_key
        # 查农历节日
        solar = Solar(date.year, date.month, date.day)
        lunar = Converter.Solar2Lunar(solar)
        lunar_key = f"{lunar.month:02d}-{lunar.day:02d}"
        if lunar_key in LUNAR_FESTIVALS:
            return LUNAR_FESTIVALS[lunar_key], lunar_key
        return None, ""
    except Exception:
        return None, ""

async def generate_festival_greetings(date_str: str, company_info: str, min_num: int = 5, max_num: int = 15) -> Tuple[str, List[str]]:
    """
    生成节日问候语列表，全部由大模型生成
    :param date_str: 日期字符串
    :param company: 公司名
    :param min_num: 最少生成几条
    :param max_num: 最多生成几条
    :return: (节日名, 问候语列表)
    """
    import json
    festival, _ = get_festival_by_date(date_str)
    if not festival:
        # 非节日，生成日常问候
        prompt = f"请根据咱们公司的资料{company_info}，生成{min_num}到{max_num}条多样化的日常问候语，每条不超过50字，内容积极正面，返回JSON数组。"
        response = await chat_qwen(prompt)
        try:
            # 清理响应文本，移除可能的markdown格式
            cleaned_response = response.strip().strip("`").strip("```json").strip("```").strip()
            greetings = json.loads(cleaned_response)
            # 确保返回的是列表
            if isinstance(greetings, list):
                return "普通日常", greetings
            else:
                return "普通日常", [str(greetings)]
        except Exception as e:
            # 如果JSON解析失败，将整个响应作为一个问候语
            return "普通日常", [response.strip()]
    
    # 节日
    num = random.randint(min_num, max_num)
    prompt = f"请根据咱们公司的资料{company_info}，针对{festival}，生成{num}条多样化的节日问候语，问候语是发送给客户的，每条不超过50字，内容积极正面，返回JSON数组。"
    response = await chat_qwen(prompt)
    try:
        # 清理响应文本，移除可能的markdown格式
        cleaned_response = response.strip().strip("`").strip("```json").strip("```").strip()
        greetings = json.loads(cleaned_response)
        # 确保返回的是列表
        if isinstance(greetings, list):
            return festival, greetings
        else:
            return festival, [str(greetings)]
    except Exception as e:
        # 如果JSON解析失败，将整个响应作为一个问候语
        return festival, [response.strip()] 