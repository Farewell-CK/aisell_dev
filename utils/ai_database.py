from core.database_core import db_manager

def create_sale_prompt_table():
    """
    创建 sale_prompt 表
    Returns:
        bool: 创建成功返回 True，失败返回 False
    """
    create_table_sql = """
    CREATE TABLE sale_prompt (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task_id INT NOT NULL,
        tenant_id INT NOT NULL,
        system_prompt TEXT NOT NULL,
        test_prompt TEXT NOT NULL,
        create_by VARCHAR(256) NOT NULL DEFAULT 'system',
        create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        update_by VARCHAR(256) DEFAULT NULL,
        update_time DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
        delete_by VARCHAR(256) DEFAULT NULL,
        delete_time DATETIME DEFAULT NULL,
        is_del TINYINT NOT NULL DEFAULT 0,
        UNIQUE KEY uk_task_tenant (task_id, tenant_id)
    );
    """

    try:
        # execute_query 方法可以执行任何 SQL 语句，包括 DDL
        db_manager.execute_query(create_table_sql)
        print("表 'sale_prompt' 创建成功！")
        return True
    except Exception as e:
        print(f"创建表 'sale_prompt' 失败: {e}")
        return False

# if __name__ == "__main__":
#     create_sale_prompt_table()