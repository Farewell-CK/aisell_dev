#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移工具
支持从MySQL迁移到SQLite或其他数据库
"""

import os
import yaml
import sqlite3
import pymysql
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, inspect
from sqlalchemy.types import String, Integer, Text, DateTime, Boolean, Float
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, source_config_path='configs/database.yaml'):
        """
        初始化数据库迁移器
        
        Args:
            source_config_path (str): 源数据库配置文件路径
        """
        self.source_config = self._load_config(source_config_path)
        self.source_engine = self._create_source_engine()
        
    def _load_config(self, config_path):
        """加载数据库配置"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_source_engine(self):
        """创建源数据库引擎"""
        db_conf = self.source_config.get('database', {})
        user = db_conf.get('username', 'root')
        password = db_conf.get('password', '')
        host = db_conf.get('host', 'localhost')
        port = db_conf.get('port', 3306)
        dbname = db_conf.get('name', 'sale')
        driver = db_conf.get('driver', 'mysql+pymysql')
        charset = db_conf.get('charset', 'utf8mb4')
        
        url = f"{driver}://{user}:{password}@{host}:{port}/{dbname}?charset={charset}"
        
        return create_engine(url, echo=False)
    
    def get_table_names(self):
        """获取源数据库中的所有表名"""
        try:
            with self.source_engine.connect() as connection:
                result = connection.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result]
                logger.info(f"找到 {len(tables)} 个表: {tables}")
                return tables
        except Exception as e:
            logger.error(f"获取表名失败: {e}")
            return []
    
    def get_table_schema(self, table_name):
        """获取表结构"""
        try:
            with self.source_engine.connect() as connection:
                # 获取表结构
                result = connection.execute(text(f"DESCRIBE {table_name}"))
                columns = []
                for row in result:
                    columns.append({
                        'name': row[0],
                        'type': row[1],
                        'null': row[2],
                        'key': row[3],
                        'default': row[4],
                        'extra': row[5]
                    })
                return columns
        except Exception as e:
            logger.error(f"获取表 {table_name} 结构失败: {e}")
            return []
    
    def get_table_data(self, table_name, limit=None):
        """获取表数据"""
        try:
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            with self.source_engine.connect() as connection:
                result = connection.execute(text(query))
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in result]
                logger.info(f"从表 {table_name} 获取了 {len(data)} 条记录")
                return data
        except Exception as e:
            logger.error(f"获取表 {table_name} 数据失败: {e}")
            return []
    
    def migrate_to_sqlite(self, target_db_path='database/sale.db', tables=None, data_limit=None):
        """
        迁移到SQLite数据库
        
        Args:
            target_db_path (str): SQLite数据库文件路径
            tables (list): 要迁移的表名列表，None表示迁移所有表
            data_limit (int): 每个表的数据限制，None表示迁移所有数据
        """
        # 确保目标目录存在
        target_dir = os.path.dirname(target_db_path)
        if target_dir:  # 只有当目录不为空时才创建
            os.makedirs(target_dir, exist_ok=True)
        
        # 创建SQLite引擎
        sqlite_url = f"sqlite:///{target_db_path}"
        target_engine = create_engine(sqlite_url, echo=False)
        
        # 获取要迁移的表
        if tables is None:
            tables = self.get_table_names()
        
        logger.info(f"开始迁移 {len(tables)} 个表到SQLite: {target_db_path}")
        
        for table_name in tables:
            try:
                logger.info(f"正在迁移表: {table_name}")
                
                # 获取表结构
                schema = self.get_table_schema(table_name)
                if not schema:
                    logger.warning(f"跳过表 {table_name}，无法获取结构")
                    continue
                
                # 创建表
                self._create_sqlite_table(target_engine, table_name, schema)
                
                # 迁移数据
                data = self.get_table_data(table_name, data_limit)
                if data:
                    self._insert_data_to_sqlite(target_engine, table_name, data)
                
                logger.info(f"表 {table_name} 迁移完成")
                
            except Exception as e:
                logger.error(f"迁移表 {table_name} 失败: {e}")
        
        logger.info("SQLite迁移完成")
        return target_db_path
    
    def _create_sqlite_table(self, engine, table_name, schema):
        """在SQLite中创建表"""
        # 构建CREATE TABLE语句
        columns = []
        for col in schema:
            col_name = col['name']
            col_type = self._convert_mysql_type_to_sqlite(col['type'])
            null_constraint = "NOT NULL" if col['null'] == 'NO' else ""
            default_value = f"DEFAULT {col['default']}" if col['default'] else ""
            
            column_def = f"{col_name} {col_type}"
            if null_constraint:
                column_def += f" {null_constraint}"
            if default_value:
                column_def += f" {default_value}"
            
            columns.append(column_def)
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        with engine.connect() as connection:
            connection.execute(text(create_sql))
            connection.commit()
    
    def _convert_mysql_type_to_sqlite(self, mysql_type):
        """将MySQL数据类型转换为SQLite类型"""
        mysql_type = mysql_type.upper()
        
        if 'INT' in mysql_type:
            return 'INTEGER'
        elif 'VARCHAR' in mysql_type or 'CHAR' in mysql_type:
            return 'TEXT'
        elif 'TEXT' in mysql_type:
            return 'TEXT'
        elif 'DATETIME' in mysql_type or 'TIMESTAMP' in mysql_type:
            return 'TEXT'
        elif 'DECIMAL' in mysql_type or 'FLOAT' in mysql_type or 'DOUBLE' in mysql_type:
            return 'REAL'
        elif 'BOOLEAN' in mysql_type or 'BOOL' in mysql_type:
            return 'INTEGER'
        else:
            return 'TEXT'
    
    def _insert_data_to_sqlite(self, engine, table_name, data):
        """将数据插入SQLite表"""
        if not data:
            return
        
        # 构建INSERT语句
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # 准备数据
        values = []
        for row in data:
            row_values = []
            for col in columns:
                value = row.get(col)
                # 处理None值
                if value is None:
                    row_values.append(None)
                else:
                    row_values.append(str(value))
            values.append(row_values)
        
        # 执行插入
        with engine.connect() as connection:
            # 逐行插入数据
            for row_values in values:
                connection.execute(text(insert_sql), row_values)
            connection.commit()
    
    def export_to_json(self, output_path='database_export.json', tables=None, data_limit=None):
        """
        导出数据库到JSON文件
        
        Args:
            output_path (str): 输出JSON文件路径
            tables (list): 要导出的表名列表
            data_limit (int): 每个表的数据限制
        """
        if tables is None:
            tables = self.get_table_names()
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'source_database': self.source_config.get('database', {}).get('name', 'unknown'),
            'tables': {}
        }
        
        for table_name in tables:
            try:
                logger.info(f"正在导出表: {table_name}")
                
                # 获取表结构
                schema = self.get_table_schema(table_name)
                
                # 获取表数据
                data = self.get_table_data(table_name, data_limit)
                
                export_data['tables'][table_name] = {
                    'schema': schema,
                    'data': data,
                    'record_count': len(data)
                }
                
                logger.info(f"表 {table_name} 导出完成，包含 {len(data)} 条记录")
                
            except Exception as e:
                logger.error(f"导出表 {table_name} 失败: {e}")
        
        # 保存到JSON文件
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
                # 自定义JSON编码器处理datetime、bytes和Decimal对象
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat() # 将 datetime 对象转换为 ISO 格式的字符串
                elif isinstance(obj, bytes):
                    return obj.decode('utf-8', errors='ignore') # 将 bytes 对象转换为字符串
                elif hasattr(obj, '__float__'):  # 处理Decimal等数值类型
                    return float(obj)
                return super().default(obj) # 对于其他类型，使用默认编码器行为
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"数据库导出完成: {output_path}")
        return output_path
    
    def generate_migration_report(self, output_path='migration_report.html'):
        """生成迁移报告"""
        tables = self.get_table_names()
        
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>数据库迁移报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .table-info {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .schema {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>数据库迁移报告</h1>
                <p><strong>源数据库:</strong> {self.source_config.get('database', {}).get('name', 'unknown')}</p>
                <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>表数量:</strong> {len(tables)}</p>
            </div>
        """
        
        for table_name in tables:
            try:
                schema = self.get_table_schema(table_name)
                data = self.get_table_data(table_name, limit=1)  # 只获取一条记录来检查
                
                report_html += f"""
                <div class="table-info">
                    <h2>表: {table_name}</h2>
                    <p><strong>字段数量:</strong> {len(schema)}</p>
                    <p><strong>数据状态:</strong> {'有数据' if data else '无数据'}</p>
                    <div class="schema">
                        <h3>表结构:</h3>
                        <table border="1" style="border-collapse: collapse; width: 100%;">
                            <tr><th>字段名</th><th>类型</th><th>允许NULL</th><th>默认值</th></tr>
                """
                
                for col in schema:
                    report_html += f"""
                        <tr>
                            <td>{col['name']}</td>
                            <td>{col['type']}</td>
                            <td>{col['null']}</td>
                            <td>{col['default'] or ''}</td>
                        </tr>
                    """
                
                report_html += """
                        </table>
                    </div>
                </div>
                """
                
            except Exception as e:
                report_html += f"""
                <div class="table-info error">
                    <h2>表: {table_name}</h2>
                    <p>错误: {str(e)}</p>
                </div>
                """
        
        report_html += """
        </body>
        </html>
        """
        logger.info(f"原数据库中表数量: {len(tables)}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        logger.info(f"迁移报告已生成: {output_path}")
        return output_path

def main():
    """主函数 - 演示如何使用迁移工具"""
    try:
        # 创建迁移器
        migrator = DatabaseMigrator()
        
        # 生成迁移报告
        migrator.generate_migration_report()
        
        # 导出到JSON
        migrator.export_to_json()
        
        # 迁移到SQLite
        sqlite_path = migrator.migrate_to_sqlite()
        
        print(f"迁移完成！SQLite数据库文件: {sqlite_path}")
        print("请更新配置文件以使用新的SQLite数据库")
        
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        print(f"迁移失败: {e}")

if __name__ == "__main__":
    main() 