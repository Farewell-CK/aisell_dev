import os
from openai import OpenAI
import json

class WeChatStyleAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://aistudio.baidu.com/llm/lmapi/v3",
        )

    def analyze_chat_style(self, image_urls):
        """分析聊天截图中的说话风格
        
        Args:
            image_urls (list): 图片URL列表
            
        Returns:
            dict: 包含状态和分析结果的字典
            {
                "status": "success" | "error",
                "message": "错误信息（如果有）",
                "data": {
                    "语言特征": {
                        "用词特点": str,
                        "句式结构": str,
                        "标点符号使用特点": str,
                        "语气词使用频率": str,
                        "表情符号使用情况": str
                    },
                    "情感特征": {
                        "情感倾向": str,
                        "情感强度": str,
                        "情感表达方式": str,
                        "情绪变化趋势": str
                    },
                    "交互特征": {
                        "回复速度": str,
                        "消息长度分布": str,
                        "话题转换频率": str,
                        "互动方式": str
                    },
                    "个性化特征": {
                        "独特的表达方式": str,
                        "习惯用语": str,
                        "口头禅": str,
                        "个人特色": str
                    },
                    "微信特有特征": {
                        "表情包使用情况": str,
                        "语音/图片/视频等多媒体使用情况": str,
                        "引用/转发消息的使用情况": str,
                        "群聊/私聊的互动特点": str
                    }
                }
            }
        """
        try:
            messages = []
            for image_url in image_urls:
                messages.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })

            prompt = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """如图所示,微信聊天记录的截图
请分析以下微信聊天记录中发送者的对话风格特征，包括但不限于：

1. 语言特征：
   - 用词特点（正式/非正式、专业术语使用频率等）
   - 句式结构（长句/短句、复杂句/简单句等）
   - 标点符号使用特点
   - 语气词使用频率
   - 表情符号使用情况

2. 情感特征：
   - 情感倾向（积极/消极/中性）
   - 情感强度
   - 情感表达方式（直接/委婉）
   - 情绪变化趋势

3. 交互特征：
   - 回复速度（根据消息时间间隔推断）
   - 消息长度分布
   - 话题转换频率
   - 互动方式（主动/被动）

4. 个性化特征：
   - 独特的表达方式
   - 习惯用语
   - 口头禅
   - 个人特色

5. 微信特有特征：
   - 表情包使用情况
   - 语音/图片/视频等多媒体使用情况
   - 引用/转发消息的使用情况
   - 群聊/私聊的互动特点

请以JSON格式输出分析结果，包含以上所有维度的具体特征描述。字数控制在1000字以内。"""
                    },
                    *messages
                ]
            }

            completion = self.client.chat.completions.create(
                model="ernie-4.5-8k-preview",
                messages=[prompt],
                stream=False,
            )

            if len(completion.choices) > 0:
                try:
                    # 尝试解析返回的JSON字符串
                    result = json.loads(completion.choices[0].message.content)
                    return {
                        "status": "success",
                        "message": "分析成功",
                        "data": result
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "message": "返回结果格式错误",
                        "data": None
                    }
            else:
                return {
                    "status": "error",
                    "message": "未获取到分析结果",
                    "data": None
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"分析过程出错: {str(e)}",
                "data": None
            }

def main():
    # 使用示例
    analyzer = WeChatStyleAnalyzer(api_key="your_api_key")
    
    # 示例图片URL列表
    image_urls = [
        "https://example.com/chat1.png",
        "https://example.com/chat2.png"
    ]
    
    result = analyzer.analyze_chat_style(image_urls)
    
    if result["status"] == "success":
        print("分析结果：")
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
    else:
        print(f"分析失败：{result['message']}")

# if __name__ == "__main__":
#     main() 