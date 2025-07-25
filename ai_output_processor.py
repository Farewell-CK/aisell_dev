import re
import json

def extract_prohibit_items(ai_output_text):
    """
    通用提取AI输出的禁止事项条目，兼容多种编号格式。
    Args:
        ai_output_text (str): AI输出的完整文本
    Returns:
        list: 包含每条内容的列表
    """
    items = []
    lines = ai_output_text.strip().split('\n')
    pattern = re.compile(r'^\s*(\d+)[\.\:、]?\s*(.*)$')
    for line in lines:
        line = line.strip()
        # 跳过标题、空行和代码块标记
        if not line or '[禁止做的事情' in line or '禁止做的事情' in line or line.startswith('```'):
            continue
        m = pattern.match(line)
        if m:
            content = m.group(2).strip()
            if content:
                items.append(content)
    return items

def restore_prohibit_format(items_list, title="[禁止做的事情]"):
    """
    将列表中的内容恢复成原始的AI输出格式。
    Args:
        items_list (list): 包含每条内容的列表
        title (str): 标题，默认为"[禁止做的事情]"
    Returns:
        str: 恢复后的原始格式文本
    """
    restored_text = f"{title}\n"
    for i, item in enumerate(items_list, 1):
        restored_text += f"{i}. {item}\n"
    return restored_text

def extract_sale_flow_items(ai_output_text):
    """
    提取AI输出的销售流程条目，转换为指定JSON格式。
    Args:
        ai_output_text (str): AI输出的销售流程文本
    Returns:
        list: 包含销售流程条目的列表，格式为[{"title":"流程标题,description":[流程描述"]}]
    """
    items = []
    lines = ai_output_text.strip().split('\n')
    current_item = None

    for line in lines:
        line = line.strip()
        # 跳过标题、空行和代码块标记
        if not line or '[销售流程]' in line or line.startswith('```'):
            continue

        # 匹配数字开头的流程标题
        title_pattern = re.compile(r'^\s*(\d+)\.\s*(.+)$')
        title_match = title_pattern.match(line)

        if title_match:
            # 如果已有当前条目，保存它
            if current_item:
                items.append(current_item)

            # 创建新条目
            title = title_match.group(2).strip()
            current_item = {"title": title, "description": []}
        elif current_item and line:
            # 将非空行添加到当前条目的描述中
            current_item["description"].append(line)

    # 添加最后一个条目
    if current_item:
        items.append(current_item)

    return items

def restore_sale_flow_format(items_list, title="[销售流程]"):
    """
    将销售流程列表恢复成原始的AI输出格式。
    Args:
        items_list (list): 包含销售流程条目的列表
        title (str): 标题，默认为"[销售流程]"
    Returns:
        str: 恢复后的原始格式文本
    """
    restored_text = f"{title}\n"
    for i, item in enumerate(items_list, 1):
        restored_text += f"{i}. {item['title']}\n"
        for desc in item['description']:
            restored_text += f"   {desc}\n"
        restored_text += "\n"
    return restored_text

# 测试示例
if __name__ == "__main__":
    # 测试禁止事项函数
    test_prohibit_output = '''[禁止做的事情]
1. 严禁以任何形式、任何语言透露自己是AI或自动化程序。
2 严禁主动询问客户的任何联系方式。
3: 严禁引用、提及、暗示任何未在“公司与产品资料”中明确存在的信息。
4、严禁承诺智云按摩椅能治疗任何疾病或医疗问题。
5.严禁虚假宣传智云按摩椅具有超出产品资料描述的功能或效果。
6 严禁对智云按摩椅的价格进行不实陈述或提供未经授权的折扣。
7.严禁在销售过程中暗示或承诺智云按摩椅能替代专业医疗或健康服务。
8.严禁将智云按摩椅与未经验证或非本公司认可的第三方产品进行捆绑销售或虚假比较。'''
    print("=== 测试禁止事项函数 ===")
    extracted_prohibit_items = extract_prohibit_items(test_prohibit_output)
    for i, item in enumerate(extracted_prohibit_items, 1):
        print(f"{i}. {item}")
    print("\n" + "="*50 + "\n")

    print("=== 测试禁止事项函数：恢复格式 ===")
    restored_prohibit_text = restore_prohibit_format(extracted_prohibit_items)
    print(restored_prohibit_text) 

    # 测试销售流程函数
    test_sale_flow_output = '''[销售流程]
1. 初步接触与兴趣激发
   行动：AI通过微信添加潜在客户为好友，发送简洁明了的自我介绍及智云按摩椅的核心价值点，附带一个引人入胜的短视频或图片展示产品特点。
   进入下一阶段标志：客户回复表示对产品感兴趣，或询问更多关于产品的细节。

2. 需求挖掘与痛点定位
   行动：AI根据客户的初步反馈，进一步询问客户的工作环境、压力状况及对放松身心的需求，尝试定位客户的具体痛点。
   进入下一阶段标志：客户描述自身业务或生活中的具体痛点，如长时间工作导致的身体疲劳、精神压力大等，并表达对解决方案的期待。

3 产品价值匹配与演示邀请
   行动：AI根据客户的痛点，详细介绍智云按摩椅如何针对这些痛点提供解决方案，强调产品的独特卖点和优势，并邀请客户参加线上产品演示或线下体验会。
   进入下一阶段标志：客户同意参加线上产品演示或询问线下体验会的具体时间和地点，或主动提出希望进一步了解产品。

4. 线下会面促成与确认
   行动：若客户对线上演示满意或直接对线下体验感兴趣，AI应立即提出促成线下会面的建议，提供几个可选的时间和地点供客户选择，并确认最终会面细节。
   进入下一阶段标志：客户同意线下会面，并确认具体的时间和地点。

5. 线索孵化与转交
   行动：在会面前，AI可适当发送提醒信息，确保客户不会遗忘。会面后，AI应收集客户的反馈，评估其购买意向，并将高质量的潜在客户线索转交给真人销售团队进行后续跟进和签约转化。
   结束标志：AI成功将高质量潜在客户线索转交给真人销售团队，并附上客户的初步反馈和评估。'''
    print("=== 测试销售流程函数：提取条目 ===")
    extracted_sale_flow_items = extract_sale_flow_items(test_sale_flow_output)
    print("提取的销售流程条目：")
    print(json.dumps(extracted_sale_flow_items, ensure_ascii=False, indent=2))
    print("\n" + "="*50 + "\n")

    print("=== 测试销售流程函数：恢复格式 ===")
    restored_sale_flow_text = restore_sale_flow_format(extracted_sale_flow_items)
    print(restored_sale_flow_text) 