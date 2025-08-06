## 概述

本文档详细说明了AI-Sell项目中的数据库操作，包括数据库配置、表结构、常用操作和最佳实践。

## 数据库配置

### 1. 配置文件

项目使用YAML格式的配置文件来管理数据库连接信息：

```yaml
# configs/database.yaml
database:
  host: "127.0.0.1"
  port: 3306
  name: "sale"
  user: ""
  password: ""
  charset: "utf8mb4"
  
connection:
  pool_size: 10
  pool_recycle: 3600
  connect_timeout: 10
  read_timeout: 30
  write_timeout: 30
```

### 2. SQLite配置

对于开发环境，也支持SQLite数据库：

```yaml
# configs/database_sqlite.yaml
database:
  type: "sqlite"
  path: "database/sale.db"
  
connection:
  timeout: 30
  check_same_thread: false
```

## 数据库表结构
查看`./数据库迁移报告.html`