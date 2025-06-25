# 导入必要的库
import pymysql
import pandas as pd
import gradio as gr

# 全局变量用于存储数据库连接
conn = None

def connect_db(host, port, user, password, database_name, charset):
    """连接到数据库并获取表名，使用用户提供的配置"""
    global conn 
    table_names_local = []
    
    # 更新的数据库连接配置
    current_db_config = {
        'host': host,
        'port': int(port) if port else 3306, # 使用默认MySQL端口（如果未提供）
        'user': user,
        'password': password,
        'database': database_name,
        'charset': charset if charset else 'utf8mb4' # 如果未提供，则使用默认字符集
    }

    # 输入验证
    if not all([host, user, database_name]): # 密码可以为空，端口和字符集有默认值
        missing_fields = []
        if not host: missing_fields.append("主机名")
        if not user: missing_fields.append("用户名")
        if not database_name: missing_fields.append("数据库名")
        
        if missing_fields:
             error_message = f"以下必填字段缺失: {', '.join(missing_fields)}。"
             print(error_message)
             # 返回给3个输出：状态消息、下拉菜单更新、密码字段更新
             return error_message, gr.update(choices=[], value=None, interactive=False), gr.update(value="") 
    
    try:
        if conn:
            try:
                conn.close()
            except Exception:
                pass 
        
        conn = pymysql.connect(**current_db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names_local = [table[0] for table in tables]
        cursor.close()
        
        if not table_names_local:
            return (f"成功连接到数据库 '{current_db_config['database']}'，但未找到任何表。", 
                    gr.update(choices=[], value=None, interactive=False), 
                    gr.update(value=password))
        
        return (
            f"成功连接到数据库 '{current_db_config['database']}'。找到 {len(table_names_local)} 个表。", 
            gr.update(choices=table_names_local, value=table_names_local[0] if table_names_local else None, interactive=True),
            gr.update(value=password) 
        )
    except pymysql.MySQLError as e: 
        error_message = f"数据库连接失败: {e}"
        print(error_message) 
        conn = None 
        return error_message, gr.update(choices=[], value=None, interactive=False), gr.update(value="") 
    except ValueError as e: 
        error_message = f"端口号无效: {e}"
        print(error_message)
        conn = None
        return error_message, gr.update(choices=[], value=None, interactive=False), gr.update(value="") 
    except Exception as e:
        error_message = f"连接时发生未知错误: {e}"
        print(error_message)
        conn = None 
        return error_message, gr.update(choices=[], value=None, interactive=False), gr.update(value="") 

def get_table_content(table_name):
    """获取并显示选定表的内容"""
    global conn
    if not conn:
        return "请先成功连接到数据库。", None 
    if not table_name: 
        return "请选择一个有效的表。", None 
    
    try:
        query = f"SELECT * FROM `{table_name}`" 
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return f"表 '{table_name}' 为空或查询没有返回数据。", df 
        return f"显示表 '{table_name}' 的内容 ({len(df)} 行):", df
    except pymysql.Error as e:
        return f"获取表 '{table_name}' 内容失败: {e}", None
    except Exception as e:
        return f"处理表 '{table_name}' 时发生未知错误: {e}", None

# 创建 Gradio 界面
# 尝试使用 gr.themes.Glass() 主题
with gr.Blocks(theme=gr.themes.Glass(), title="数据库可视化工具") as app:
    gr.Markdown("# 🗂️ 数据库表内容可视化工具")
    gr.Markdown("在下方配置数据库连接信息，然后连接并浏览表中的数据。")

    with gr.Accordion("⚙️ 数据库连接配置", open=False): # 默认不展开
        with gr.Row():
            with gr.Column(scale=2):
                db_host = gr.Textbox(label="主机名 (Host)", placeholder="例如：127.0.0.1", value="120.77.8.73")
                db_user = gr.Textbox(label="用户名 (User)", placeholder="例如：root", value="root")
                db_name = gr.Textbox(label="数据库名 (Database)", placeholder="例如：mydatabase", value="sale")
            with gr.Column(scale=1):
                db_port = gr.Number(label="端口 (Port)", value=9010, minimum=1, maximum=65535, step=1)
                db_password = gr.Textbox(label="密码 (Password)", type="password", placeholder="输入数据库密码", value="sale159753")
                db_charset = gr.Textbox(label="字符集 (Charset)", placeholder="例如：utf8mb4", value="utf8mb4")
        connect_button = gr.Button("🔗 连接到数据库并加载表", variant="primary") # 添加variant
    
    status_message = gr.Textbox(label="ℹ️ 连接状态", interactive=False, lines=1, max_lines=1)

    gr.Markdown("---") # 添加一个分隔线

    with gr.Row():
        table_dropdown_component = gr.Dropdown(label="📜 选择一个表进行查看", choices=[], interactive=False)

    output_message = gr.Textbox(label="📢 操作信息", interactive=False, lines=1, max_lines=1)
    output_df = gr.DataFrame(label="📊 表内容", wrap=True) # 允许换行并设置固定高度

    # 定义交互行为
    connect_button.click(
        fn=connect_db,
        inputs=[db_host, db_port, db_user, db_password, db_name, db_charset],
        outputs=[status_message, table_dropdown_component, db_password]
    )

    table_dropdown_component.change(
        fn=get_table_content,
        inputs=[table_dropdown_component], 
        outputs=[output_message, output_df]
    )

    with gr.Accordion("📖 使用说明与注意", open=False):
        gr.Markdown(
            """
            **使用说明:**
            1. 展开 "数据库连接配置" 部分，填写您的数据库详细信息 (主机名、用户名和数据库名是必填项)。
            2. 点击 "连接到数据库并加载表" 按钮。
            3. 查看 "连接状态" 获取反馈。如果连接成功，"选择一个表进行查看" 下拉菜单将填充表名并变为可交互。
            4. 从下拉菜单中选择一个表，其内容将自动显示在 "表内容" 区域。
            
            **注意:**
            - 确保数据库服务可访问，并且防火墙设置允许连接。
            - 如果连接失败，密码字段可能会被清空以确保安全。
            - 对于非常大的表，加载可能需要一些时间。
            """
        )

# 运行 Gradio 应用
if __name__ == '__main__':
    print("Gradio 应用已准备就绪。正在启动...")
    app.launch(server_name="0.0.0.0", server_port="11450")
