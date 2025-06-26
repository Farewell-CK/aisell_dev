import asyncio
import json
from typing import Dict, List, Optional
from utils.config_loader import ConfigLoader
from utils.chat import chat_qwen
from utils.db_queries import select_wechat_name, select_knowledge

class OpeningGenerator:
    """聊天开场白生成器"""
    
    def __init__(self):
        self.config = ConfigLoader()
        self.api_key = self.config.get_api_key('qwen', 'api_key')
    
    async def generate_personalized_opening(
        self, 
        tenant_id: int,
        task_id: int,
        wechat_id: int,
        # session_id: str,
        # customer_info: Dict[str, str],
        # sales_info: Dict[str, str],
        # context: str = ""
    ) -> Dict[str, str]:
        """
        生成个性化开场白
        
        Args:
            customer_info: 客户信息字典，包含姓名、公司、职位等
            sales_info: 销售信息字典，包含姓名、公司、产品等
            context: 额外上下文信息
            
        Returns:
            Dict: 包含开场白和状态信息的字典
        """
        wechat_name = select_wechat_name(tenant_id, wechat_id)
        knowledge = select_knowledge(tenant_id, task_id)
        prompt = self._build_personalized_prompt(wechat_name, knowledge)
        
        try:
            response = await chat_qwen(self.api_key, prompt)
            return {
                "status": "success",
                "opening": response.strip(),
                "type": "personalized"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成个性化开场白失败: {str(e)}",
                "type": "personalized"
            }
    
    async def generate_industry_opening(
        self, 
        industry: str,
        product_info: Dict[str, str],
        sales_info: Dict[str, str]
    ) -> Dict[str, str]:
        """
        生成行业针对性开场白
        
        Args:
            industry: 目标行业
            product_info: 产品信息
            sales_info: 销售信息
            
        Returns:
            Dict: 包含开场白和状态信息的字典
        """
        prompt = self._build_industry_prompt(industry, product_info, sales_info)
        
        try:
            response = await chat_qwen(self.api_key, prompt)
            return {
                "status": "success",
                "opening": response.strip(),
                "type": "industry"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成行业开场白失败: {str(e)}",
                "type": "industry"
            }
    
    async def generate_event_opening(
        self, 
        event_type: str,
        event_info: Dict[str, str],
        sales_info: Dict[str, str]
    ) -> Dict[str, str]:
        """
        生成基于事件的开场白（如展会、会议等）
        
        Args:
            event_type: 事件类型（展会、会议、活动等）
            event_info: 事件信息
            sales_info: 销售信息
            
        Returns:
            Dict: 包含开场白和状态信息的字典
        """
        prompt = self._build_event_prompt(event_type, event_info, sales_info)
        
        try:
            response = await chat_qwen(self.api_key, prompt)
            return {
                "status": "success",
                "opening": response.strip(),
                "type": "event"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成事件开场白失败: {str(e)}",
                "type": "event"
            }
    
    async def generate_referral_opening(
        self, 
        referrer_info: Dict[str, str],
        customer_info: Dict[str, str],
        sales_info: Dict[str, str]
    ) -> Dict[str, str]:
        """
        生成推荐人开场白
        
        Args:
            referrer_info: 推荐人信息
            customer_info: 客户信息
            sales_info: 销售信息
            
        Returns:
            Dict: 包含开场白和状态信息的字典
        """
        prompt = self._build_referral_prompt(referrer_info, customer_info, sales_info)
        
        try:
            response = await chat_qwen(self.api_key, prompt)
            return {
                "status": "success",
                "opening": response.strip(),
                "type": "referral"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成推荐开场白失败: {str(e)}",
                "type": "referral"
            }
    
    async def generate_multiple_openings(
        self, 
        customer_info: Dict[str, str],
        sales_info: Dict[str, str],
        opening_types: List[str] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        生成多种类型的开场白
        
        Args:
            customer_info: 客户信息
            sales_info: 销售信息
            opening_types: 开场白类型列表，默认为所有类型
            
        Returns:
            Dict: 包含多种开场白的字典
        """
        if opening_types is None:
            opening_types = ["personalized", "industry", "event", "referral"]
        
        results = []
        
        for opening_type in opening_types:
            if opening_type == "personalized":
                result = await self.generate_personalized_opening(customer_info, sales_info)
            elif opening_type == "industry":
                result = await self.generate_industry_opening(
                    customer_info.get("industry", ""), 
                    sales_info, 
                    sales_info
                )
            elif opening_type == "event":
                result = await self.generate_event_opening(
                    "general", 
                    {"event_name": "初次接触"}, 
                    sales_info
                )
            elif opening_type == "referral":
                result = await self.generate_referral_opening(
                    {"name": "朋友推荐"}, 
                    customer_info, 
                    sales_info
                )
            else:
                result = {
                    "status": "error",
                    "message": f"不支持的开场白类型: {opening_type}",
                    "type": opening_type
                }
            
            results.append(result)
        
        return {
            "status": "success",
            "openings": results
        }
    
    def _build_personalized_prompt(self, wechat_name: str, knowledge: str) -> str:
        """构建个性化开场白提示词"""
        return f"""
你是一位专业的销售开场白设计师。请基于以下信息，生成自然、专业、个性化的微信开场白。

## 角色信息
- 微信昵称：{wechat_name}
- 公司信息：{knowledge}

## 开场白要求
1. **昵称处理规则**：
   - 如果昵称是真实姓名（如：中科小苏、张三、李四），在开场白中要使用真实姓名
   - 如果昵称不是真实姓名（如：落日余晖、星辰大海），则不要提及昵称

2. **开场白特点**：
   - 自然友好，不突兀
   - 体现专业性和个性化
   - 避免过度推销
   - 为后续沟通留下话题
   - 每个开场白控制在15字以内

3. **输出格式**：
   请直接输出JSON格式的开场白列表：
   ```json
   ["开场白1", "开场白2", "开场白3", "开场白4", "开场白5"]
   ```

请直接输出JSON格式的开场白列表，不要包含其他说明文字。
"""
    
    def _build_industry_prompt(self, industry: str, product_info: Dict[str, str], sales_info: Dict[str, str]) -> str:
        """构建行业针对性开场白提示词"""
        return f"""
你是一位专业的销售开场白设计师。请基于以下信息，生成一个针对{industry}行业的微信开场白。

行业信息：{industry}

产品信息：
- 产品名称：{product_info.get('product', '')}
- 产品优势：{product_info.get('advantage', '')}
- 适用场景：{product_info.get('scenarios', '')}

销售信息：
- 姓名：{sales_info.get('name', '销售')}
- 公司：{sales_info.get('company', '')}

要求：
1. 体现对{industry}行业的了解
2. 突出产品在该行业的价值
3. 自然引出客户痛点
4. 为后续深入交流做铺垫
5. 控制在50字以内

请直接输出开场白内容，不要包含其他说明文字。
"""
    
    def _build_event_prompt(self, event_type: str, event_info: Dict[str, str], sales_info: Dict[str, str]) -> str:
        """构建事件开场白提示词"""
        return f"""
你是一位专业的销售开场白设计师。请基于以下信息，生成一个基于{event_type}事件的微信开场白。

事件信息：
- 事件类型：{event_type}
- 事件名称：{event_info.get('event_name', '')}
- 事件时间：{event_info.get('event_time', '')}
- 事件地点：{event_info.get('event_location', '')}

销售信息：
- 姓名：{sales_info.get('name', '销售')}
- 公司：{sales_info.get('company', '')}
- 产品：{sales_info.get('product', '')}

要求：
1. 自然提及{event_type}事件
2. 建立共同话题
3. 体现专业性和亲和力
4. 为后续产品介绍做铺垫
5. 控制在50字以内

请直接输出开场白内容，不要包含其他说明文字。
"""
    
    def _build_referral_prompt(self, referrer_info: Dict[str, str], customer_info: Dict[str, str], sales_info: Dict[str, str]) -> str:
        """构建推荐人开场白提示词"""
        return f"""
你是一位专业的销售开场白设计师。请基于以下信息，生成一个基于推荐人的微信开场白。

推荐人信息：
- 姓名：{referrer_info.get('name', '朋友')}
- 关系：{referrer_info.get('relationship', '朋友')}

客户信息：
- 姓名：{customer_info.get('name', '客户')}
- 公司：{customer_info.get('company', '')}

销售信息：
- 姓名：{sales_info.get('name', '销售')}
- 公司：{sales_info.get('company', '')}
- 产品：{sales_info.get('product', '')}

要求：
1. 自然提及推荐人
2. 建立信任基础
3. 避免过度推销
4. 为后续沟通做铺垫
5. 控制在50字以内

请直接输出开场白内容，不要包含其他说明文字。
"""

# 便捷函数
async def generate_opening(
    opening_type: str,
    customer_info: Dict[str, str],
    sales_info: Dict[str, str],
    **kwargs
) -> Dict[str, str]:
    """
    便捷的开场白生成函数
    
    Args:
        opening_type: 开场白类型 ("personalized", "industry", "event", "referral")
        customer_info: 客户信息
        sales_info: 销售信息
        **kwargs: 其他参数
        
    Returns:
        Dict: 包含开场白和状态信息的字典
    """
    generator = OpeningGenerator()
    
    if opening_type == "personalized":
        return await generator.generate_personalized_opening(customer_info, sales_info, kwargs.get('context', ''))
    elif opening_type == "industry":
        return await generator.generate_industry_opening(
            customer_info.get('industry', ''), 
            sales_info, 
            sales_info
        )
    elif opening_type == "event":
        return await generator.generate_event_opening(
            kwargs.get('event_type', 'general'),
            kwargs.get('event_info', {}),
            sales_info
        )
    elif opening_type == "referral":
        return await generator.generate_referral_opening(
            kwargs.get('referrer_info', {}),
            customer_info,
            sales_info
        )
    else:
        return {
            "status": "error",
            "message": f"不支持的开场白类型: {opening_type}",
            "type": opening_type
        } 