import re
import json

def convert_to_chinese_num(number: int) -> str:
    """
    将个位数阿拉伯数字转换为中文数字。

    Args:
        number (int): 要转换的个位数阿拉伯数字（0-9）。

    Returns:
        str: 对应的中文数字。如果数字超出范围，返回空字符串。
    """
    num_map = {
        0: '零',
        1: '一',
        2: '二',
        3: '三',
        4: '四',
        5: '五',
        6: '六',
        7: '七',
        8: '八',
        9: '九'
    }
    
    # 使用字典的 .get() 方法，如果数字不在映射中，可以返回一个默认值（例如，空字符串或None）
    return num_map.get(number, '')


def format_forbidden_content(forbidden_items: list) -> str:
    """
    将禁止事项列表格式化为指定的Markdown文本。

    Args:
        forbidden_items: 一个包含禁止事项字符串的列表。

    Returns:
        格式化后的Markdown字符串。
    """
    if not forbidden_items:
        return "### 8. 禁止做的事情：\n暂无禁止事项。"

    formatted_string = "### 8. 禁止做的事情：\n"
    for i, item in enumerate(forbidden_items, 1):
        formatted_string += f"{i}. {item}\n"
    return formatted_string

def format_sale_process(process_data: list[dict]) -> str:
    """
    将销售流程数据格式化为指定的Markdown文本。

    Args:
        process_data: 一个包含销售流程字典的列表，每个字典有 'title', 'text', 'sort'。

    Returns:
        格式化后的Markdown字符串。
    """
    if not process_data:
        return "### 7. 销售流程：\n暂无销售流程信息。"

    formatted_string = "### 7. 销售流程：\n\n"

    for item in process_data:
        title = item.get('title', '未知标题')
        text = item.get('text', '')
        title_num = convert_to_chinese_num(item.get('sort', 0))
        # 根据换行符分割text内容，并格式化为列表项
        text_lines = text.strip().split('\n')
        formatted_string += f"#### {title_num}. {title}\n\n"
        formatted_string += f"- **目标**: {text_lines[0]} \n- **行动**: {text_lines[1]} \n- **话术示例**:\n  >{text_lines[2]}\n"
        formatted_string += f"- **关键**: {text_lines[3]}\n\n"
        formatted_string += "---\n" # 每个流程步骤后添加分隔符

    return formatted_string.strip() # 移除末尾多余的换行和分隔符 


async def extract_prohibit_items(ai_output_text):
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

async def extract_sale_flow_items(ai_output_text):
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
        items_list (list): 包含销售流程条目的列表，每个条目包含 'title', 'description', 'sort'
        title (str): 标题，默认为"[销售流程]"
    Returns:
        str: 恢复后的原始格式文本
    """
    restored_text = f"{title}\n"
    
    # 按sort字段排序
    sorted_items = sorted(items_list, key=lambda x: x.get('sort', 0))
    
    for i, item in enumerate(sorted_items, 1):
        title = item.get('title', '')
        description = item.get('description', '')
        
        # 处理description字段，可能是字符串或列表
        if isinstance(description, str):
            # 如果是字符串，清理可能的方括号和引号
            desc_text = description.strip()
            # 移除开头和结尾的方括号和引号
            if desc_text.startswith("['") and desc_text.endswith("']"):
                desc_text = desc_text[2:-2]
            elif desc_text.startswith('["') and desc_text.endswith('"]'):
                desc_text = desc_text[2:-2]
            elif desc_text.startswith('[') and desc_text.endswith(']'):
                desc_text = desc_text[1:-1]
        elif isinstance(description, list):
            # 如果是列表，将其连接成字符串
            desc_text = '\n'.join(description)
        else:
            desc_text = str(description)
        
        # 尝试解析描述文本，提取行动和标志信息
        # 如果描述中包含"行动："和"标志："，则保持原格式
        if "行动：" in desc_text and "标志：" in desc_text:
            formatted_desc = desc_text
        elif "行动：" in desc_text and "进入下一阶段标志：" in desc_text:
            formatted_desc = desc_text
        else:
            # 如果没有明确的行动和标志结构，尝试智能解析
            # 这里可以根据实际需求添加更复杂的解析逻辑
            formatted_desc = desc_text
        
        restored_text += f"{i}. {title}\n"
        restored_text += f"   {formatted_desc}\n\n"
    
    return restored_text.strip()