from tools.database import DatabaseManager
from typing import Dict, Any
from utils.logger_config import get_database_logger

db_manager = DatabaseManager()
logger = get_database_logger()


def insert_sale_prompt(tenant_id: int, task_id: int, system_prompt: str, test_prompt: str, create_by: str = 'system') -> bool:
    """
    插入销售提示词。
    """
    insert_sql = f"""
    INSERT INTO sale_prompt (tenant_id, task_id, test_prompt, system_prompt, create_by, create_time, update_time, is_del)
    VALUES ({tenant_id}, {task_id}, '{test_prompt}', '{system_prompt}', '{create_by}', NOW(), NOW(), 0);
    """
    db_manager.execute_insert(insert_sql)
    return True
def update_sale_system_prompt(tenant_id: int, task_id: int, system_prompt: str, create_by: str = 'system') -> bool:
    """
    更新销售提示词。
    """
    update_sql = f"""
    UPDATE sale_prompt SET system_prompt = '{system_prompt}', update_time = NOW() WHERE tenant_id = {tenant_id} AND task_id = {task_id} AND is_del = 0;
    """
    db_manager.execute_update(update_sql)
    return True

def select_sale_system_prompt(tenant_id: int, task_id: int) -> str:
    """
    查询销售提示词。
    """
    select_sql = f"""
    SELECT system_prompt FROM sale_prompt WHERE tenant_id = {tenant_id} AND task_id = {task_id} AND is_del = 0;
    """
    result = db_manager.execute_query(select_sql)
    if result:
        return result[0]
    else:
        return None

def insert_sale_ai_data_record(ai_type: int, ai_text: str, ai_status: int, tenant_id: int, create_by: str = 'system') -> bool:
    """
    向 sale_ai_data 表中插入一条新的 AI 数据记录。

    Args:
        db_manager (DatabaseManager): DatabaseManager 类的实例。
        ai_type (int): AI 数据类型。
        ai_text (str): AI 文本内容。
        ai_status (int): AI 处理状态。
        tenant_id (int): 租户ID。
        create_by (str, optional): 创建人。默认为 'system'。

    Returns:
        bool: True 表示插入成功，False 表示插入失败。
    """
    # SQL INSERT 语句
    # 注意：为了防止SQL注入，对字符串类型的值进行单引号转义。
    # 在生产环境中，更推荐使用参数绑定（如：VALUES (:type, :text, ...)）
    escaped_ai_text = ai_text.replace("'", "''")
    escaped_create_by = create_by.replace("'", "''")

    query = f"""
    INSERT INTO sale_ai_data (
        type,
        ai_text,
        ai_status,
        tenant_id,
        create_by,
        is_del -- 明确指定 is_del，使用其默认值 0
    ) VALUES (
        {ai_type},
        '{escaped_ai_text}',
        {ai_status},
        {tenant_id},
        '{escaped_create_by}',
        0
    );
    """
    try:
        db_manager.execute_query(query)
        logger.info(f"成功插入 AI 数据记录：tenant_id={tenant_id}, type={ai_type}, status={ai_status}")
        return True
    except Exception as e:
        logger.error(f"插入 AI 数据记录失败：{e}", exc_info=True)
        return False
    
def update_sale_ai_data_status(record_id: int, tenant_id: int, new_ai_status: int = 1, ai_text: str = None) -> bool:
    """
    更新 sale_ai_data 表中指定记录的 AI 处理状态。

    Args:
        record_id (int): 要更新的记录的 ID。
        tenant_id (int): 租户ID。
        new_ai_status (int): 新的 AI 处理状态。
        ai_text (str, optional): 新的 AI 文本内容。

    Returns:
        bool: True 表示更新成功，False 表示更新失败。
    """
    

    query = f"""
    UPDATE sale_ai_data
    SET
        ai_status = {new_ai_status},
        ai_text = '{ai_text}',
        update_time = CURRENT_TIMESTAMP
    WHERE
        id = {record_id}
        AND tenant_id = {tenant_id}
        AND is_del = 0; -- 仅更新未被逻辑删除的记录
    """
    try:
        db_manager.execute_update(query)
        logger.info(f"成功更新 AI 数据记录 ID={record_id} 的状态为 {new_ai_status}")
        return True
    except Exception as e:
        logger.error(f"更新 AI 数据记录 ID={record_id} 状态失败：{e}", exc_info=True)
        return False
    

def insert_file_description(tenant_id: int, task_id: int, file_id: int, file_name: str, file_description: str):
    """
    插入文件描述信息。
    """
    insert_sql = """
    INSERT INTO file_description (tenant_id, task_id, file_id, file_name, file_description)
    VALUES (%s, %s, %s, %s, %s)
    """
    db_manager.execute_query(insert_sql, (tenant_id, task_id, file_id, file_name, file_description))

def insert_chat_style(tenant_id: int, task_id: int, chat_style: str):
    """
    插入聊天风格信息。
    """
    insert_sql = """
    INSERT INTO chat_style (tenant_id, task_id, chat_style)
    VALUES (%s, %s, %s)
    """
    db_manager.execute_query(insert_sql, (tenant_id, task_id, chat_style))

def insert_customer_behavior(tenant_id: int, belong_wechat_id: int, wechat_id: int, customer_behavior_title: str, customer_behavior_content: str, create_by: str = 'system') -> str:
    """
    插入客户行为信息。 
    Args:
        tenant_id: 租户id
        belong_wechat_id: 所属微信id
        wechat_id: 微信id
        customer_behavior_title: 客户行为标题
        customer_behavior_content: 客户行为内容
        create_by: 创建人
    return: 插入客户行为成功
    """
    insert_sql = f"""
            INSERT INTO sale_wechat_behavior (
            belong_wechat_id,
            wechat_id,
            title,
            content,
            create_by,
            tenant_id
            -- create_time 和 is_del 通常有默认值，可省略
        ) VALUES (
            {belong_wechat_id},
            {wechat_id},
            {customer_behavior_title},
            {customer_behavior_content},
            {create_by},
            {tenant_id}
        );
    """
    db_manager.execute_insert(insert_sql)
    return "插入客户行为成功"
def insert_customer_portrait(tenant_id: int, belong_wechat_id: int, wechat_id: int, phone: str, name: str, industry: str, department: str, company: str, post: str, company_size: str, city: str, create_by: str = 'system') -> str:
    """
    插入客户画像信息。
    Args:
        tenant_id: 租户id
        belong_wechat_id: 所属微信id
        wechat_id: 微信id
        phone: 手机号
        name: 姓名
        industry: 行业
        department: 部门
        company: 公司
        post: 职位
        company_size: 公司规模
        city: 城市
        create_by: 创建人
    return: 插入客户画像成功
    """
    insert_sql = f"""
    INSERT INTO sale_wechat_contact (
        belong_wechat_id,   -- 联系人所属的微信账号ID（如机器人账号）
        wechat_id,          -- 联系人本身的微信ID
        name,               -- 姓名
        phone,              -- 手机号
        industry,           -- 行业
        department,         -- 部门
        company,            -- 公司
        post,               -- 职位
        company_size,       -- 公司规模
        city,               -- 城市
        create_by,          -- 创建人
        tenant_id           -- 租户ID
        -- 其他字段如 create_time 和 is_del 通常有默认值，可省略
    ) VALUES (
        {belong_wechat_id},
        {wechat_id},
        {name},
        {phone},
        {industry},
        {department},
        {company},
        {post},
        {company_size},
        {city},
        {create_by},
        {tenant_id}
    );
    """
    db_manager.execute_insert(insert_sql)
    return "插入客户画像成功"

def get_task_status(record_id: int, tenant_id: int) -> Dict[str, Any]:
    """
    获取任务处理状态。

    Args:
        record_id (int): 任务记录ID。
        tenant_id (int): 租户ID。

    Returns:
        Dict[str, Any]: 包含任务状态信息的字典，如果未找到则返回None。
    """
    query = f"""
    SELECT id, tenant_id, type, ai_status, ai_text, create_time, update_time
    FROM sale_ai_data
    WHERE id = {record_id}
    AND tenant_id = {tenant_id}
    AND is_del = 0
    """
    try:
        result = db_manager.fetch_one(query)
        if result:
            return {
                "id": result[0],
                "tenant_id": result[1],
                "type": result[2],
                "status": result[3],
                "ai_text": result[4],
                "create_time": result[5],
                "update_time": result[6]
            }
        else:
            return None
    except Exception as e:
        logger.error(f"查询任务状态失败：{e}", exc_info=True)
        return None

def get_last_insert_id() -> int:
    """
    获取最后插入记录的ID。

    Returns:
        int: 最后插入记录的ID。
    """
    query = "SELECT LAST_INSERT_ID()"
    try:
        result = db_manager.fetch_one(query)
        if result:
            return result[0]
        else:
            return 0
    except Exception as e:
        logger.error(f"获取最后插入ID失败：{e}", exc_info=True)
        return 0