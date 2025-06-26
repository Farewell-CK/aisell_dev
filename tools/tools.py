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

# # 示例
# print(f"1 转换为：{convert_to_chinese_num(1)}")
# print(f"2 转换为：{convert_to_chinese_num(2)}")
# print(f"5 转换为：{convert_to_chinese_num(5)}")
# print(f"0 转换为：{convert_to_chinese_num(0)}")
# print(f"10 转换为（超出范围）：{convert_to_chinese_num(10)}") # 会返回空字符串


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


