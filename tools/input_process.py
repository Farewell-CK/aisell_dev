import os
import requests
from datetime import datetime
from http import HTTPStatus
from openai import OpenAI
from dashscope.audio.asr import Transcription
import json
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

qwen_api_key = os.getenv("Qwen_API_KEY")
# 若没有将API Key配置到环境变量中，需将下面这行代码注释放开，并将apiKey替换为自己的API Key
import dashscope
dashscope.api_key = qwen_api_key

# 语音转文本工具

def speech_to_text(audio_url: str) -> dict:
    """
    将音频文件转换为文本

    Args:
        audio_url (str): 音频文件的URL

    Returns:
        dict: 一个包含识别结果的字典。
              包含一个'status'键，值为'success'或'error'。
              如果'success',包含一个'text'键，值为识别结果。
              如果'error',包含一个'error_message'键，值为错误信息。
    """
    try:
        transcribe_response = Transcription.async_call(
        model='paraformer-v2',
        file_urls=[audio_url])

        while True:
            if transcribe_response.output.task_status == 'SUCCEEDED' or transcribe_response.output.task_status == 'FAILED':
                break
            transcribe_response = Transcription.fetch(task=transcribe_response.output.task_id)

        if transcribe_response.status_code == HTTPStatus.OK:
            text_url = transcribe_response.output["results"][0]["transcription_url"]
            status = transcribe_response.output["results"][0]["subtask_status"]
            response = requests.get(text_url, timeout=10)

            # 检查请求是否成功
            response.raise_for_status()

            # 解析JSON内容
            data = response.json()
            text = data["transcripts"][0]["text"]
            # print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
            print('transcription done!')
        return {"status": "success", "text": text}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
    
# 文本转语音工具
def text_to_speech(text: str) -> dict:
    """
    将文本转换为语音

    Args:
        text (str): 需要转换的文本

    Returns:
        dict: 一个包含语音文件URL的字典。
              包含一个'status'键，值为'success'或'error'。
              如果'success',包含一个'audio_url'键，值为语音文件的URL。
              如果'error',包含一个'error_message'键，值为错误信息。
    """
    try:
        client = OpenAI(
            api_key=os.getenv("Qwen_API_KEY"),
            base_url=os.getenv("Qwen_BASE_URL"),
        )

        completion = client.chat.completions.create(
            model="qwen-vl-plus-latest",
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful assistant."}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{text}"},
                    ],
                },
            ],
        )
        audio_url = completion.choices[0].message.content
        return {"status": "success", "audio_url": audio_url}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
# 图像描述工具
def image_comprehension(image_url: str) -> dict:
    """
    将图像文件转换为文本描述，描述图像内容。

    Args:
        image_url (str): 需要识别的图像文件的URL。

    Returns:
        dict: 一个包含识别结果的字典。
              包含一个'status'键，值为'success'或'error'。
              如果'success',包含一个'image_description'键，值为图片描述结果。
              如果'error',包含一个'error_message'键，值为错误信息。
    """
    try:

        client = OpenAI(
            api_key=os.getenv("Qwen_API_KEY"),
            base_url=os.getenv("Qwen_BASE_URL"),
        )

        completion = client.chat.completions.create(
            model="qwen-vl-plus-latest",
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful assistant."}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image_url}"
                            },
                        },
                        {"type": "text", "text": "图中描绘的是什么景象?"},
                    ],
                },
            ],
        )

        # print(completion.choices[0].message.content)
        return {"status": "success", "image_description": completion.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
    
# 视频理解工具
def video_comprehension(video_url: str) -> dict:
    """
    通过分析视频的视觉和音频组件来了解视频的内容。

    Args:
        video_url (str): 需要分析的视频的 URL。

    Returns:
        dict: 一个包含视频理解结果的字典。
             包含一个'status'键，值为'success'或'error'。
             如果'success'，包含一个'video_description'键，值为视频描述结果。
             如果'error'，包含一个'error_message'键，值为错误信息。
    """
    try:
        client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("Qwen_API_KEY"),
        base_url=os.getenv("Qwen_BASE_URL"),
        )
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {"role": "system",
                "content": [{"type": "text","text": "You are a helpful assistant."}]},
                {"role": "user","content": [{
                    # 直接传入视频文件时，请将type的值设置为video_url
                    # 使用OpenAI SDK时，视频文件默认每间隔0.5秒抽取一帧，且不支持修改，如需自定义抽帧频率，请使用DashScope SDK.
                    "type": "video_url",            
                    "video_url": {"url": video_url}},
                    {"type": "text","text": "这段视频的内容是什么?"}]
                }]
        )
        # print(completion.choices[0].message.content)
        return {"status": "success", "video_description": completion.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

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

def get_detailed_time():
  """
  获取当前详细时间，并返回包含一个格式化的字符串的字典。

  Returns:
    dict: 包含当前详细时间的字典。
  """
  now = datetime.datetime.now()
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
  return {"status": "success", "report": formatted_time}

def analyze_chat_style(image_path: str) -> dict:
    """
    从微信聊天截图中提取并分析发送者的对话风格。

    Args:
        image_path (str): 聊天截图文件的本地路径。

    Returns:
        dict: 一个包含分析结果的字典。
              包含一个'status'键，值为'success'或'error'。
              如果'success',包含一个'style_analysis'键，值为对话风格分析结果。
              如果'error',包含一个'error_message'键，值为错误信息。
    """
    try:
        # 使用微信聊天解析器解析截图
        from utils.wechat_chat_parser import WeChatChatParser
        parser = WeChatChatParser()
        parse_result = parser.parse_chat_image(image_path)
        
        if parse_result["status"] == "error":
            return parse_result

        # 使用对话风格分析器分析发送者的消息
        from utils.dialogue_style_analyzer import DialogueStyleAnalyzer
        analyzer = DialogueStyleAnalyzer(os.getenv("Ernie_API_KEY"))
        style_analysis = analyzer.analyze_sender_style(parse_result["messages"])

        return style_analysis

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

