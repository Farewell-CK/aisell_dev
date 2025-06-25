from tools.database import DatabaseManager
from tools.tools import format_forbidden_content, format_sale_process
db_manager = DatabaseManager()


def select_ai_data(tenant_id: int, task_id: int) -> list[dict]:
    """
    根据租户ID和任务ID，查询任务的AI发送的文件数据。
    """
    try:
        query = f"""
                SELECT
                    sad.ai_text,
                    sad.url
                FROM
                    sale_ai_data sad
                JOIN
                    sale_task_data std ON sad.id = std.data_id
                JOIN
                    sale_task st ON std.task_id = st.id
                WHERE
                    st.task_id = {task_id}
                    AND st.tenant_id = {tenant_id}
                    AND sad.is_del = 0
                    AND std.is_del = 0
                    AND sad.ai_status = 2
                    AND st.is_del = 0;
                """
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return [f"查询AI发送的文件数据失败: {str(e)}"]

def select_base_info(tenant_id: int, task_id: int) -> list[dict]:
    """
    根据租户ID和任务ID，查询任务的基本信息。
    """
    try:
        query = f"""
            SELECT DISTINCT
                swa.wechat_nickname
            FROM
                sale_wechat_account swa
            JOIN
                sale_user su ON swa.tenant_id = su.tenant_id
            JOIN
                sale_user_role sur ON su.id = sur.user_id
            WHERE
                su.tenant_id = {tenant_id}       -- 筛选特定租户
                AND spr.id = {task_id}         -- 筛选特定角色
                AND swa.is_del = 0                -- 确保微信账号未被逻辑删除
                AND su.is_del = 0                 -- 确保用户未被逻辑删除
                AND sur.is_del = 0                -- 确保用户-角色关联未被逻辑删除
        """
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return f"查询任务的基本信息失败: {str(e)}"

def select_wechat_name(tenant_id: int,  wechat_id: str) -> str:
    """
    根据租户ID、任务ID和微信ID，查询微信昵称。
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
        wechat_id: 微信ID
    Returns:
        str: 微信昵称
    """
    try:
        query = f"""
            SELECT
                swa.wechat_nickname
            FROM
                sale_wechat_account swa
            WHERE
                swa.tenant_id = {tenant_id}
                AND swa.wechat_id = '{wechat_id}'
        """
        result = db_manager.execute_query(query)
        return result[0]['wechat_nickname']
    except Exception as e:
        return f"查询微信昵称失败: {str(e)}"

def select_talk_style(tenant_id: int, task_id: int) -> list[dict]:
    """
    根据租户ID和任务ID，查询任务的聊天风格。

    Args:
        tenant_id: 租户ID
        task_id: 任务ID

    Returns:
        list[dict]: 任务的聊天风格
    """
    try:
        query = f"SELECT talk_style FROM sale_strategy WHERE tenant_id = {tenant_id} AND task_id = {task_id}"
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return f"查询任务的聊天风格失败: {str(e)}"
    
def select_knowledge(tenant_id: int, task_id: int) -> list[dict]:
    """
    根据租户ID和任务ID，查询任务的知识库。

    Args:
        tenant_id: 租户ID
        task_id: 任务ID

    Returns:
        list[dict]: 任务的知识库
    """
    try:
        query = f"""
            SELECT
                sk.title,
                sk.text
            FROM
                sale_knowledge sk
            JOIN
                sale_task_knowledge stk ON sk.id = stk.knowledge_id
            JOIN
                sale_task st ON stk.task_id = st.id
            WHERE
                st.tenant_id = {tenant_id}
                AND st.id = {task_id}
                AND sk.is_del = 0  -- 考虑逻辑删除，只查询未删除的知识
                AND stk.is_del = 0 -- 考虑逻辑删除，只查询未删除的任务-知识关联
                AND st.is_del = 0; -- 考虑逻辑删除，只查询未删除的任务
"""
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return f"查询任务的知识库失败: {str(e)}"
    
def select_product(tenant_id: int, task_id: int) -> list[dict]:
    """
    根据租户ID和任务ID，查询任务的产品。

    Args:
        tenant_id: 租户ID
        task_id: 任务ID

    Returns:
        list[dict]: 任务的产品
    """
    try:
        query = f"""
            SELECT
                sp.id,
                sp.name,
                sp.type,
                sp.description,
                sp.url,
                sp.status,
                sp.price_unit,
                sp.sale_unit,
                sp.standard_price,
                sp.lowest_price
            FROM
                sale_product sp
            JOIN
                sale_task_product stp ON sp.id = stp.product_id
            JOIN
                sale_task st ON stp.task_id = st.id
            WHERE
                st.tenant_id = {tenant_id}
                AND st.id = {task_id}
                AND sp.is_del = 0   -- 考虑逻辑删除，只查询未删除的产品
                AND stp.is_del = 0  -- 考虑逻辑删除，只查询未删除的任务-产品关联
                AND st.is_del = 0;  -- 考虑逻辑删除，只查询未删除的任务
"""
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return f"查询任务的产品失败: {str(e)}" 
    
def select_sale_prompt(tenant_id : int, task_id : int) -> str:
    """
    查询销售提示词, 测试使用
    Args:
        tenant_id: 租户ID
        task_id: 任务ID
    Returns:
        str: 销售提示词
    """
    try:
        query = f"""
            SELECT
                sp.test_prompt
            FROM
                sale_prompt sp
            WHERE
                sp.task_id = {task_id}
                AND sp.tenant_id = {tenant_id}
                AND sp.is_del = 0;
        """
        result = db_manager.execute_query(query)
        return result[0]['test_prompt']
    except Exception as e:
        return f"查询销售提示词失败: {str(e)}"

def select_sale_system_prompt(tenant_id : int, task_id : int) -> str:
    """
    查询销售系统提示词
    """
    try:
        query = f"""
            SELECT
                sp.system_prompt
            FROM
                sale_prompt sp
            WHERE
                sp.task_id = {task_id}
                AND sp.tenant_id = {tenant_id}
                AND sp.is_del = 0;
        """
        result = db_manager.execute_query(query)
        return result[0]['system_prompt']
    except Exception as e:
        return f"查询销售系统提示词失败: {str(e)}"

def select_forbidden_content(tenant_id : int, task_id : int) -> str:
    """
    查询禁止内容
    """
    try:
        query = f"""
            SELECT
                sf.text AS forbidden_content
            FROM
                sale_forbidden sf
            JOIN
                sale_strategy ss ON sf.strategy_id = ss.id
            WHERE
                ss.tenant_id = {tenant_id}
                AND ss.task_id = {task_id}
                AND sf.is_del = 0  -- 确保禁止事项未被逻辑删除
                AND ss.is_del = 0; -- 确保销售策略未被逻辑删除
        """
        result = db_manager.execute_query(query)
        forbidden_content = []
        if result:
            for item in result:
                forbidden_content.append(item['forbidden_content'])
        return format_forbidden_content(forbidden_content)
    except Exception as e:
        return [f"查询禁止内容失败: {str(e)}"]
    
def select_sale_process(tenant_id : int, task_id : int) -> str:
    """
    查询销售流程
    """
    try:
        query = f"""
            SELECT
                sp.title AS process_title,
                sp.text AS process_text,
                sp.sort
            FROM
                sale_process sp
            JOIN
                sale_strategy ss ON sp.strategy_id = ss.id
            WHERE
                ss.tenant_id = {tenant_id}
                AND ss.task_id = {task_id}
                AND sp.is_del = 0
                AND ss.is_del = 0
            ORDER BY
                sp.sort;
        """
        result = db_manager.execute_query(query)
        sale_process = []
        if result:
            for item in result:
                sale_process.append({
                    'title': item['process_title'],
                    'text': item['process_text'],
                    'sort': item['sort']
                })
        return format_sale_process(sale_process)
    except Exception as e:
        return [f"查询销售流程失败: {str(e)}"]

def select_collaborate_matters(tenant_id : int, task_id : int) -> list[dict]:
    """
    根据租户ID和任务ID，查询对应的协作事项的ID、标题和内容。

    Args:
        db_manager (DatabaseManager): DatabaseManager 类的实例。
        tenant_id (int): 租户ID。
        task_id (int): 任务ID。

    Returns:
        list[dict]: 包含协作事项信息（id, title, text）的字典列表。
                    如果查询失败或无结果，返回空列表（或根据需要处理异常）。
    """
    try:
        query = f"""
            SELECT
                sc.id AS collaborate_id,
                sc.title,
                sc.text
            FROM
                sale_collaborate sc
            JOIN
                sale_task st ON sc.task_id = st.id
            WHERE
                st.tenant_id = {tenant_id}
                AND st.id = {task_id}
                AND sc.is_del = 0
                AND st.is_del = 0;
            """
        result = db_manager.execute_query(query)
        return result
    except Exception as e:
        return [f"查询协作事项失败: {str(e)}"]
            

def insert_sale_prompt( task_id: int, tenant_id: int, system_prompt: str, test_prompt: str, create_by: str = 'system'):
    """
    向 sale_prompt 表中插入一条新的提示词记录。

    Args:
        db_manager (DatabaseManager): DatabaseManager 类的实例。
        task_id (int): 任务ID。
        tenant_id (int): 租户ID。
        system_prompt (str): 系统提示内容。
        test_prompt (str): 测试提示内容。
        create_by (str, optional): 创建人。默认为 'system'。

    Returns:
        bool: True 表示插入成功，False 表示插入失败（例如违反唯一约束）。
    """
    # SQL INSERT 语句
    query = f"""
    INSERT INTO sale_prompt (
        task_id,
        tenant_id,
        system_prompt,
        test_prompt,
        create_by
    ) VALUES (
        {task_id},
        {tenant_id},
        '{system_prompt.replace("'", "''")}', -- 转义单引号以防止SQL注入问题
        '{test_prompt.replace("'", "''")}',    -- 同上
        '{create_by.replace("'", "''")}'
    );
    """
    try:
        # execute_query 方法可以执行 INSERT 语句
        # 对于 INSERT, UPDATE, DELETE 操作，execute_query 返回的列表通常是空的
        # 但如果执行成功，不会抛出异常
        db_manager.execute_query(query)
        print(f"成功插入提示词：任务ID={task_id}, 租户ID={tenant_id}") # Successfully inserted prompt
        return True
    except Exception as e:
        print(f"插入提示词失败，任务ID={task_id}, 租户ID={tenant_id}: {e}") # Failed to insert prompt
        return False
    
def update_sale_prompt(task_id: int, tenant_id: int, system_prompt: str = None, test_prompt: str = None, update_by: str = None):
    """
    根据 task_id 和 tenant_id 更新 sale_prompt 表中的提示词记录。

    Args:
        db_manager (DatabaseManager): DatabaseManager 类的实例。
        task_id (int): 任务ID (用于定位记录)。
        tenant_id (int): 租户ID (用于定位记录)。
        system_prompt (str, optional): 新的系统提示内容。如果为 None 则不更新。
        test_prompt (str, optional): 新的测试提示内容。如果为 None 则不更新。
        update_by (str, optional): 更新人。

    Returns:
        bool: True 表示更新成功，False 表示更新失败。
    """
    updates = []
    if system_prompt is not None:
        safe_system_prompt = system_prompt.replace("'", "''")
        updates.append(f"system_prompt = '{safe_system_prompt}'")
    if test_prompt is not None:
        safe_test_prompt = test_prompt.replace("'", "''")
        updates.append(f"test_prompt = '{safe_test_prompt}'")
    if update_by is not None:
        safe_update_by = update_by.replace("'", "''")
        updates.append(f"update_by = '{safe_update_by}'")
    # update_time 字段已经在 CREATE TABLE 语句中设置为 ON UPDATE CURRENT_TIMESTAMP，所以无需手动设置

    if not updates:
        print("没有提供要更新的字段。") # No fields provided for update.
        return False

    update_clause = ", ".join(updates)
    
    # SQL UPDATE 语句
    query = f"""
    UPDATE sale_prompt
    SET
        {update_clause}
    WHERE
        task_id = {task_id}
        AND tenant_id = {tenant_id}
        AND is_del = 0; -- 仅更新未被逻辑删除的记录
    """
    try:
        db_manager.execute_query(query)
        print(f"成功更新提示词：任务ID={task_id}, 租户ID={tenant_id}") # Successfully updated prompt
        # return True
    except Exception as e:
        print(f"更新提示词失败，任务ID={task_id}, 租户ID={tenant_id}: {e}") # Failed to update prompt
        pass

    