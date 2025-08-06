#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
将MySQL数据库迁移到SQLite，包含数据脱敏和限制功能
"""

import os
import sys
import shutil
import hashlib
import random
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.database_migration import DatabaseMigrator
from sqlalchemy import create_engine, text
import json
import logging

logger = logging.getLogger(__name__)

class SensitiveDataMigrator(DatabaseMigrator):
    """敏感数据处理迁移器"""
    
    def __init__(self, source_config_path='configs/database.yaml'):
        super().__init__(source_config_path)
        
        # 定义敏感字段映射
        self.sensitive_fields = {
            # 微信相关敏感字段
            'wechat_id': 'wechat_id',
            'wechat_no': 'wechat_no', 
            'wechat_nickname': 'wechat_nickname',
            'wechat_group_id': 'wechat_group_id',
            'wechat_group_nickname': 'wechat_group_nickname',
            'belong_wechat_id': 'belong_wechat_id',
            'source_wechat_id': 'source_wechat_id',
            'sender_wechat_id': 'sender_wechat_id',
            
            # 公司相关敏感字段
            'company_name': 'company_name',
            'company_id': 'company_id',
            
            # 用户相关敏感字段
            'user_id': 'user_id',
            'username': 'username',
            'name': 'name',
            'mobile_no': 'mobile_no',
            'phone': 'phone',
            'email': 'email',
            
            # 聊天记录相关敏感字段
            'content': 'content',
            'text': 'text',
            'message': 'message',
            'chat_content': 'chat_content',
            'reply_content': 'reply_content',
            
            # 其他敏感字段
            'password': 'password',
            'token': 'token',
            'api_key': 'api_key',
            'secret': 'secret'
        }
        
        # 脱敏数据缓存，确保相同值脱敏后保持一致
        self.masking_cache = {}
    
    def mask_sensitive_data(self, value, field_name):
        """
        对敏感数据进行脱敏处理
        
        Args:
            value: 原始值
            field_name: 字段名
            
        Returns:
            脱敏后的值
        """
        if value is None:
            return None
        
        # 检查是否是敏感字段
        if field_name.lower() not in [k.lower() for k in self.sensitive_fields.keys()]:
            return value
        
        # 创建缓存键
        cache_key = f"{field_name}_{str(value)}"
        
        # 如果已经脱敏过，返回缓存的结果
        if cache_key in self.masking_cache:
            return self.masking_cache[cache_key]
        
        # 根据字段类型进行不同的脱敏处理
        if field_name.lower() in ['wechat_id', 'wechat_no', 'belong_wechat_id', 'source_wechat_id', 'sender_wechat_id']:
            # 微信ID脱敏：保持格式但替换内容
            masked_value = f"wx_{hashlib.md5(str(value).encode()).hexdigest()[:8]}"
        elif field_name.lower() in ['wechat_nickname', 'wechat_group_nickname']:
            # 微信昵称脱敏
            masked_value = f"用户_{hashlib.md5(str(value).encode()).hexdigest()[:6]}"
        elif field_name.lower() in ['company_name', 'name']:
            # 公司名和姓名脱敏
            masked_value = f"公司_{hashlib.md5(str(value).encode()).hexdigest()[:6]}"
        elif field_name.lower() in ['mobile_no', 'phone']:
            # 手机号脱敏：保留前3位和后4位
            phone_str = str(value)
            if len(phone_str) >= 7:
                masked_value = phone_str[:3] + '*' * (len(phone_str) - 7) + phone_str[-4:]
            else:
                masked_value = '*' * len(phone_str)
        elif field_name.lower() in ['email']:
            # 邮箱脱敏：保留@前的第一个字符和@后的域名
            email_str = str(value)
            if '@' in email_str:
                username, domain = email_str.split('@', 1)
                masked_value = f"{username[0]}***@{domain}"
            else:
                masked_value = '***@example.com'
        elif field_name.lower() in ['password', 'token', 'api_key', 'secret']:
            # 密码等敏感信息完全脱敏
            masked_value = '***MASKED***'
        elif field_name.lower() in ['content', 'text', 'message', 'chat_content', 'reply_content']:
            # 聊天内容脱敏：保留长度但替换内容
            content_str = str(value)
            if len(content_str) > 20:
                masked_value = f"[脱敏内容_{len(content_str)}字符]"
            else:
                masked_value = '[脱敏内容]'
        else:
            # 其他敏感字段：使用哈希脱敏
            masked_value = f"MASKED_{hashlib.md5(str(value).encode()).hexdigest()[:8]}"
        
        # 缓存脱敏结果
        self.masking_cache[cache_key] = masked_value
        return masked_value
    
    def get_table_data(self, table_name, limit=10):
        """
        获取表数据，限制为10行，并对敏感字段进行脱敏
        
        Args:
            table_name (str): 表名
            limit (int): 数据限制，默认10行
            
        Returns:
            list: 脱敏后的数据列表
        """
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            
            with self.source_engine.connect() as connection:
                result = connection.execute(text(query))
                columns = result.keys()
                data = []
                
                for row in result:
                    row_dict = dict(zip(columns, row))
                    
                    # 对敏感字段进行脱敏
                    masked_row = {}
                    for field_name, value in row_dict.items():
                        masked_row[field_name] = self.mask_sensitive_data(value, field_name)
                    
                    data.append(masked_row)
                
                logger.info(f"从表 {table_name} 获取了 {len(data)} 条记录（已脱敏）")
                return data
                
        except Exception as e:
            logger.error(f"获取表 {table_name} 数据失败: {e}")
            return []
    
    def migrate_to_sqlite(self, target_db_path='database/sale.db', tables=None):
        """
        迁移到SQLite数据库，每个表限制10行数据并脱敏
        
        Args:
            target_db_path (str): SQLite数据库文件路径
            tables (list): 要迁移的表名列表，None表示迁移所有表
        """
        # 确保目标目录存在
        target_dir = os.path.dirname(target_db_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        
        # 创建SQLite引擎
        sqlite_url = f"sqlite:///{target_db_path}"
        target_engine = create_engine(sqlite_url, echo=False)
        
        # 获取要迁移的表
        if tables is None:
            tables = self.get_table_names()
        
        logger.info(f"开始迁移 {len(tables)} 个表到SQLite（每个表限制10行，已脱敏）: {target_db_path}")
        
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
                
                # 迁移数据（限制10行并脱敏）
                data = self.get_table_data(table_name, limit=10)
                if data:
                    self._insert_data_to_sqlite(target_engine, table_name, data)
                
                logger.info(f"表 {table_name} 迁移完成（{len(data)} 条记录）")
                
            except Exception as e:
                logger.error(f"迁移表 {table_name} 失败: {e}")
        
        logger.info("SQLite迁移完成（数据已脱敏）")
        return target_db_path
    
    def export_to_json(self, output_path='database_export_masked.json', tables=None):
        """
        导出数据库到JSON文件，包含脱敏数据
        
        Args:
            output_path (str): 输出JSON文件路径
            tables (list): 要导出的表名列表
        """
        if tables is None:
            tables = self.get_table_names()
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'source_database': self.source_config.get('database', {}).get('name', 'unknown'),
            'data_masked': True,
            'data_limit_per_table': 10,
            'tables': {}
        }
        
        for table_name in tables:
            try:
                logger.info(f"正在导出表: {table_name}")
                
                # 获取表结构
                schema = self.get_table_schema(table_name)
                
                # 获取表数据（限制10行并脱敏）
                data = self.get_table_data(table_name, limit=10)
                
                export_data['tables'][table_name] = {
                    'schema': schema,
                    'data': data,
                    'record_count': len(data),
                    'data_masked': True
                }
                
                logger.info(f"表 {table_name} 导出完成，包含 {len(data)} 条脱敏记录")
                
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
                    return obj.isoformat()
                elif isinstance(obj, bytes):
                    return obj.decode('utf-8', errors='ignore')
                elif hasattr(obj, '__float__'):
                    return float(obj)
                return super().default(obj)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"数据库导出完成（已脱敏）: {output_path}")
        return output_path

def backup_original_config():
    """备份原始配置文件"""
    original_config = 'configs/database.yaml'
    backup_config = f'configs/database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    
    if os.path.exists(original_config):
        shutil.copy2(original_config, backup_config)
        print(f"✅ 原始配置文件已备份到: {backup_config}")
        return backup_config
    return None

def switch_to_sqlite():
    """切换到SQLite配置"""
    sqlite_config = 'configs/database_sqlite.yaml'
    target_config = 'configs/database.yaml'
    
    if os.path.exists(sqlite_config):
        shutil.copy2(sqlite_config, target_config)
        print("✅ 已切换到SQLite配置")
        return True
    else:
        print("❌ SQLite配置文件不存在")
        return False

def main():
    """主函数"""
    print("🚀 开始数据库迁移流程（包含数据脱敏）...")
    print("=" * 60)
    print("📋 迁移设置:")
    print("   - 每个表限制10行数据")
    print("   - 敏感字段自动脱敏")
    print("   - 微信ID、昵称、公司名等敏感信息将被替换")
    print("=" * 60)
    
    try:
        # 1. 备份原始配置
        backup_file = backup_original_config()
        
        # 2. 恢复MySQL配置用于迁移
        if backup_file:
            shutil.copy2(backup_file, 'configs/database.yaml')
            print("✅ 已恢复MySQL配置用于迁移")
        
        # 3. 创建敏感数据处理迁移器
        print("📊 正在分析源数据库...")
        migrator = SensitiveDataMigrator()
        
        # 4. 生成迁移报告
        print("📋 生成迁移报告...")
        report_path = migrator.generate_migration_report()
        print(f"✅ 迁移报告已生成: {report_path}")
        
        # 5. 导出数据到JSON（脱敏）
        print("📤 导出数据到JSON（已脱敏）...")
        json_path = migrator.export_to_json()
        print(f"✅ 数据导出完成: {json_path}")
        
        # 6. 迁移到SQLite（脱敏）
        print("🔄 开始迁移到SQLite（数据已脱敏）...")
        sqlite_path = migrator.migrate_to_sqlite()
        print(f"✅ SQLite数据库创建完成: {sqlite_path}")
        
        # 7. 切换到SQLite配置
        print("⚙️ 切换到SQLite配置...")
        if switch_to_sqlite():
            print("✅ 配置切换完成")
        else:
            print("❌ 配置切换失败")
        
        print("=" * 60)
        print("🎉 迁移完成！")
        print(f"📁 SQLite数据库文件: {sqlite_path}")
        print(f"📋 迁移报告: {report_path}")
        print(f"📤 数据备份（已脱敏）: {json_path}")
        if backup_file:
            print(f"💾 原始配置备份: {backup_file}")
        
        print("\n🔒 数据安全说明:")
        print("   - 所有敏感数据已脱敏处理")
        print("   - 每个表只保留10行示例数据")
        print("   - 微信ID、昵称、公司名等敏感信息已被替换")
        print("   - 聊天记录内容已被脱敏")
        
        print("\n📝 下一步操作:")
        print("1. 测试应用是否正常工作")
        print("2. 如果测试通过，可以删除MySQL数据库")
        print("3. 如果需要回滚，可以恢复备份的配置文件")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        print("请检查数据库连接配置和网络连接")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 