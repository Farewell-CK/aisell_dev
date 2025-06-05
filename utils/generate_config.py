from prompts.prompts import strategy_prompt, role_prompt
import openai as OpenAI
import os

client = OpenAI(
    api_key=os.getenv("Qwen_API_KEY"),
    base_url=os.getenv("Qwen_BASE_URL")
)

def generate_strategy(company_info, product_info):
    """
    生成销售策略
    
    Args:
        company_info: 公司信息
        product_info: 产品信息

    Returns:
        strategy: 销售策略
    """

    prompt = strategy_prompt.format(company_info=company_info, product_info=product_info)
    response = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[ {"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content



def generate_role(base_info, company_info, product_info, communication_style, sales_strategy, prohibited_actions):
    """
    生成销售角色
    
    Args:
        base_info: 销售人员的基本信息
        company_info: 公司信息
        product_info: 产品信息
        communication_style: 沟通风格
        sales_strategy: 销售策略
        prohibited_actions: 禁止事项
    
    Returns:
        role: 销售角色
    """
    
    base_info = base_info.replace("{{", "").replace("}}", "")
    prompt = role_prompt.format(base_info=base_info, company_info=company_info, product_info=product_info, communication_style=communication_style, sales_strategy=sales_strategy, prohibited_actions=prohibited_actions)
    response = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[ {"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


