# 数据库迁移指南

本指南将帮助您将MySQL数据库迁移到SQLite，以解决连接超时问题。

## 📋 迁移概述

### 当前问题
- MySQL数据库连接经常超时
- 网络连接不稳定
- 数据库服务器负载较高

### 解决方案
- 迁移到SQLite本地数据库
- 减少网络依赖
- 提高应用稳定性

## 🚀 迁移步骤

### 1. 准备工作

确保您的环境满足以下要求：
```bash
# 检查Python依赖
pip install sqlalchemy pymysql pyyaml pandas
```

### 2. 执行迁移

运行迁移脚本：
```bash
python migrate_to_sqlite.py
```

这个脚本会：
- ✅ 备份原始MySQL配置
- 📊 分析源数据库结构
- 📋 生成迁移报告
- 📤 导出数据到JSON备份
- 🔄 迁移数据到SQLite
- ⚙️ 切换到SQLite配置

### 3. 验证迁移结果

运行测试脚本：
```bash
python test_sqlite_migration.py
```

这个脚本会：
- 🔍 测试SQLite连接
- 📊 验证表数据完整性
- 📁 检查数据库文件
- 🔄 与MySQL数据对比

### 4. 测试应用功能

启动您的应用并测试主要功能：
```bash
python main.py
```

## 🔧 配置文件说明

### MySQL配置 (原始)
```yaml
# configs/database.yaml
database:
  host: 120.77.8.73
  port: 9010
  username: root
  password: sale159753
  name: sale
  driver: 'mysql+pymysql'
  charset: 'utf8mb4'
  pool_size: 10
  max_overflow: 30
  pool_recycle: 3600
  pool_pre_ping: true
  pool_timeout: 30
  connect_timeout: 10
```

### SQLite配置 (迁移后)
```yaml
# configs/database.yaml
database:
  driver: 'sqlite'
  database_path: 'database/sale.db'
  pool_size: 1
  max_overflow: 0
  pool_recycle: 3600
  pool_pre_ping: true
  pool_timeout: 30
  connect_timeout: 10
```

## 📁 生成的文件

迁移过程会生成以下文件：

1. **SQLite数据库文件**
   - `database/sale.db` - 主要的SQLite数据库文件

2. **备份文件**
   - `configs/database_backup_YYYYMMDD_HHMMSS.yaml` - MySQL配置备份
   - `database_export.json` - 数据导出备份

3. **报告文件**
   - `migration_report.html` - 详细的迁移报告

## 🔄 回滚操作

如果迁移后出现问题，可以使用回滚脚本：

```bash
python rollback_migration.py
```

这个脚本会：
- 💾 备份当前SQLite配置
- 🔄 恢复MySQL配置
- 📝 提供清理建议

## ⚠️ 注意事项

### 数据安全
- 迁移前请确保数据已备份
- 建议在测试环境中先进行迁移
- 保留原始MySQL数据库直到确认一切正常

### 性能考虑
- SQLite适合中小型应用
- 并发访问能力有限
- 文件大小会随着数据增长

### 兼容性
- 某些MySQL特有功能可能不支持
- 数据类型会自动转换
- 索引和约束会简化处理

## 🛠️ 故障排除

### 常见问题

1. **连接失败**
   ```
   ❌ 数据库连接失败
   ```
   - 检查网络连接
   - 验证数据库配置
   - 确认数据库服务状态

2. **数据丢失**
   ```
   ❌ 迁移后数据不完整
   ```
   - 检查JSON备份文件
   - 重新运行迁移脚本
   - 对比原始数据

3. **应用错误**
   ```
   ❌ 应用启动失败
   ```
   - 检查配置文件格式
   - 验证数据库文件权限
   - 查看应用日志

### 调试命令

```bash
# 检查SQLite文件
ls -la database/sale.db

# 查看数据库内容
sqlite3 database/sale.db ".tables"

# 检查配置文件
cat configs/database.yaml

# 查看迁移报告
open migration_report.html
```

## 📞 技术支持

如果遇到问题，请：

1. 查看迁移报告 (`migration_report.html`)
2. 检查应用日志 (`logs/` 目录)
3. 运行测试脚本 (`test_sqlite_migration.py`)
4. 必要时使用回滚脚本

## 🎯 迁移优势

### 解决的问题
- ✅ 消除网络连接超时
- ✅ 提高应用稳定性
- ✅ 简化部署和维护
- ✅ 减少服务器依赖

### 新的特性
- 📁 本地文件数据库
- 🔒 更好的数据安全性
- ⚡ 更快的查询速度
- 💾 自动备份机制

---

**迁移完成后，您的应用将使用本地SQLite数据库，不再依赖远程MySQL服务器。** 