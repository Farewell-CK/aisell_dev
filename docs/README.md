# AI-Sell API 文档

本目录包含了AI-Sell项目中所有服务的详细API文档。

## 文档结构

### 核心服务
- [主对话服务](./main-service.md) - 智能对话核心API
- [文件描述服务](./description-service.md) - 文件智能描述和总结API
- [开场白生成服务](./opening-service.md) - 个性化开场白和问候语生成API
- [角色创建服务](./role-service.md) - 销售角色创建和管理API

### 辅助服务
- [微信风格服务](./wechat-style-service.md) - 微信风格消息生成API
- [聊天测试服务](./chat-test-service.md) - 聊天功能测试API
- [文件读取服务](./file-reader-service.md) - 文件读取和处理API

### 工具和配置
- [数据库操作](./database-operations.md) - 数据库相关操作说明
- [配置说明](./configuration.md) - 项目配置和部署说明

## 快速开始

1. 查看 [主对话服务](./main-service.md) 了解核心对话功能
2. 查看 [配置说明](./configuration.md) 了解如何配置和部署
3. 根据需要查看其他服务的API文档

## 通用说明

### 请求格式
所有API都使用JSON格式进行数据交换，请求头应包含：
```
Content-Type: application/json
```

### 响应格式
标准响应格式：
```json
{
  "status": "success|error",
  "message": "响应消息",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "唯一请求ID"
}
```

### 错误处理
当API调用失败时，会返回相应的HTTP状态码和错误信息：
- 400: 请求参数错误
- 401: 认证失败
- 404: 资源不存在
- 500: 服务器内部错误

### 认证
部分API需要API密钥认证，请在请求头中包含：
```
Authorization: Bearer your_api_key
```

## 联系支持

如有问题，请通过以下方式联系：
- GitHub Issues: [项目地址](https://github.com/Farewell-CK/aisell_dev)
- 邮箱: 请通过GitHub Issues提交 