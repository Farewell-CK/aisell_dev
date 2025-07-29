#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
将MySQL数据库迁移到SQLite
"""

import os
import sys
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.database_migration import DatabaseMigrator

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
    print("🚀 开始数据库迁移流程...")
    print("=" * 50)
    
    try:
        # 1. 备份原始配置
        backup_file = backup_original_config()
        
        # 2. 恢复MySQL配置用于迁移
        if backup_file:
            shutil.copy2(backup_file, 'configs/database.yaml')
            print("✅ 已恢复MySQL配置用于迁移")
        
        # 3. 创建迁移器
        print("📊 正在分析源数据库...")
        migrator = DatabaseMigrator()
        
        # 3. 生成迁移报告
        print("📋 生成迁移报告...")
        report_path = migrator.generate_migration_report()
        print(f"✅ 迁移报告已生成: {report_path}")
        
        # 4. 导出数据到JSON
        print("📤 导出数据到JSON...")
        json_path = migrator.export_to_json()
        print(f"✅ 数据导出完成: {json_path}")
        
        # 5. 迁移到SQLite
        print("🔄 开始迁移到SQLite...")
        sqlite_path = migrator.migrate_to_sqlite()
        print(f"✅ SQLite数据库创建完成: {sqlite_path}")
        
        # 6. 切换到SQLite配置
        print("⚙️ 切换到SQLite配置...")
        if switch_to_sqlite():
            print("✅ 配置切换完成")
        else:
            print("❌ 配置切换失败")
        
        print("=" * 50)
        print("🎉 迁移完成！")
        print(f"📁 SQLite数据库文件: {sqlite_path}")
        print(f"📋 迁移报告: {report_path}")
        print(f"📤 数据备份: {json_path}")
        if backup_file:
            print(f"💾 原始配置备份: {backup_file}")
        
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