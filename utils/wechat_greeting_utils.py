import json
from typing import List, Tuple, Optional
from utils.chat import chat_ernie
from utils.db_queries import select_knowledge, select_product, select_ai_data, select_wechat_name
import logging

logger = logging.getLogger(__name__)

async def generate_wechat_greeting_message(tenant_id: str, task_id: str, wechat_id: str) -> Tuple[str, List[str]]:
    """
    生成一条微信添加好友时的打招呼话术
    :param tenant_id: 租户ID
    :param task_id: 任务ID
    :param wechat_id: 微信ID
    :return: (状态, 话术列表)
    """
    try:
        # 获取微信昵称、公司信息、产品信息和可发送资料
        wechat_name = select_wechat_name(int(tenant_id), wechat_id)
        company_info = select_knowledge(int(tenant_id), int(task_id))
        product_info = select_product(int(tenant_id), int(task_id))
        ai_data = select_ai_data(int(tenant_id), int(task_id))
        logger.info(f"微信昵称: {wechat_name}")
        logger.info(f"公司信息: {company_info}")
        logger.info(f"产品信息: {product_info}")
        logger.info(f"可发送资料: {ai_data}")
        # 构建提示词
        prompt = _build_wechat_greeting_prompt(wechat_name, company_info, product_info, ai_data)
        # 调用AI生成话术
        response = await chat_ernie(prompt)
        try:
            # 清理响应文本，移除可能的markdown格式
            cleaned_response = response.strip().strip("`").strip("```json").strip("```").strip()
            messages = json.loads(cleaned_response)
            # 只取第一条
            if isinstance(messages, list) and messages:
                return "success", [str(messages[0])]
            elif isinstance(messages, str):
                return "success", [messages]
            else:
                return "success", [str(messages)]
        except Exception as e:
            # 如果JSON解析失败，将整个响应作为一个话术
            return "success", [response.strip()]
    except Exception as e:
        return "error", [f"生成微信打招呼话术失败: {str(e)}"]

def _build_wechat_greeting_prompt(wechat_name: str, company_info: List[dict], product_info: List[dict], ai_data: List[dict]) -> str:
    """
    构建微信打招呼提示词，只生成一句话
    """
    # 格式化公司信息
    company_text = ""
    if company_info and isinstance(company_info, list):
        for item in company_info:
            if isinstance(item, dict):
                title = item.get('title', '')
                text = item.get('text', '')
                company_text += f"【{title}】{text}\n"
    
    # 格式化产品信息
    product_text = ""
    if product_info and isinstance(product_info, list):
        for item in product_info:
            if isinstance(item, dict):
                name = item.get('name', '')
                description = item.get('description', '')
                product_text += f"【{name}】{description}\n"
    
    # 格式化可发送资料
    materials_text = ""
    if ai_data and isinstance(ai_data, list):
        for item in ai_data:
            if isinstance(item, dict):
                ai_text = item.get('ai_text', '')
                url = item.get('url', '')
                materials_text += f"资料名称：{ai_text}，发送时机：适合时发送\n"
    
    prompt = f"""
### **角色与目标**
你是一个专业的AI销售文案专家。
你的核心任务是根据用户提供的公司及产品资料，生成一句高度精准的微信添加好友时的打招呼话术，目标是让客户知道你是做什么业务的，有需要可以找你。

### **背景信息**
*   **使用渠道**： 微信添加好友时的验证消息。
*   **沟通时机**： 这是客户添加微信好友时发送的第一条消息。

### **输入信息**
你将接收到四份核心资料：

【微信昵称】
{wechat_name}

【公司资料】
{company_text}

【产品资料】
{product_text}

【可发给客户的资料清单】
{materials_text if materials_text else "本次输入未提供此清单，视为没有任何可外发的资料。"}

### **工作流程与指令**
你的任务是执行以下步骤：
1.  **深度分析资料**: 仔细研读**[公司与产品资料]**，需要精准识别出：
    *   **行业领域**: (例如：金融、医疗、教育、SaaS软件等)
    *   **产品/服务的核心价值与局限性**: 它能做什么，同样重要的是，它不能做什么。
    *   **客户画像**: 目标客户是谁？他们关心什么？他们有哪些知识盲区？
    *   **商业模式**: (例如：客单价高低、是否有复杂的定价或折扣策略等)
2.  **设计打招呼方案**：自行定义打招呼应遵循的核心原则（例如：简洁明了、价值导向、建立信任、避免销售感等），设计一套高成功率的打招呼方案。该方案由两部分构成：
    *   **话术文本**:用于直接发送的文字。
    *   **打招呼资料**: 如果有【可发给客户的资料清单】，则判断是否需要发送资料，需要则从中选择最合适的一个。
    *   **设计注意一**: 如果微信昵称是真实姓名（如：中科小苏、张三、李四），在打招呼中要使用真实姓名；如果昵称不是真实姓名（如：落日余晖、星辰大海），则不要提及昵称。
    *   **设计注意二**: 话术文本中必须包含公司或产品名称。
    *   **设计注意三**: 打招呼话术文本避免使用句号"。"结尾，以避免生硬感。
    *   **设计注意四**: 微信验证消息有字数限制，需要简洁明了。

### **约束与规则**
*   **长度**： 最终生成的文案，总字数必须严格控制在30字以内。
*   **语气**： 必须专业、尊重、且自然。
*   **格式**： 
1.  只输出最终的打招呼话术文本。
2.  如果判断需要在发送话术文本后立即发送一份资料，则输出需要发送文件名称。

请只生成1条微信打招呼话术，返回JSON数组格式：
```json
[
    "话术1"
]
```

请直接输出JSON格式的话术列表，不要包含其他说明文字。
"""
    
    return prompt 