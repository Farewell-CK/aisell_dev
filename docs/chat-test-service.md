# 聊天测试服务 API 文档

## 概述

聊天测试服务提供聊天功能的测试和验证功能，帮助开发者测试和调试聊天相关的功能。

## 服务信息

- **服务名称**: 聊天测试服务
- **端口**: 根据启动脚本配置
- **协议**: HTTP/HTTPS
- **数据格式**: JSON

## API 端点

### 1. 聊天功能测试

#### 请求信息
- **方法**: `POST`
- **路径**: `/chat`
- **描述**: 测试聊天功能，模拟用户与AI的对话

#### 请求参数

**请求体** (JSON):
```json
{
    "query": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "你好"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "这个你直接用上次发送给你的响应中assistant_message字段，直接替代这一整个body"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
                    }
                },
                {
                    "type": "text",
                    "text": "图中描绘的是什么景象?"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "图中描绘的是一个温馨的海滩场景。具体细节如下：\n\n1. **人物与宠物**：\n   - 一位女性坐在沙滩上，穿着格子衬衫和深色裤子，显得休闲而放松。\n   - 她旁边有一只金毛犬，狗狗戴着彩色的项圈，正用前爪轻轻触碰女性的手掌，仿佛在进行“握手”的互动。\n\n2. **环境**：\n   - 场景发生在海滩上，背景是广阔的海洋和柔和的天空，海水轻轻拍打着岸边。\n   - 沙滩上的光线温暖柔和，可能是日出或日落时分，营造出一种宁静而美好的氛围。\n\n3. **情感表达**：\n   - 女性面带微笑，眼神温柔地看着狗狗，表现出对狗狗的喜爱和亲密感。\n   - 狗狗的姿态也很友好，显示出与人类之间的良好互动和信任。\n\n4. **整体氛围**：\n   - 整个画面充满了和谐、温馨和自然的气息，展现了人与宠物之间深厚的情感联系，以及大自然的美好景色。\n\n这幅图像传递了一种平静、愉悦和亲密的感觉，让人感受到人与自然、人与宠物之间的美好时光。"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "这个女性的头发是什么颜色？"
                }
            ]
        }
    ],
    "tenant_id": "1",
    "task_id": "70",
    "session_id": "session_abc",
    "model": "qwen"
}
```


#### 响应参数

**成功响应** (200):
```json
{
            "response": json_response,
            "status": "success"
        }
```

### 5. 健康检查

#### 请求信息
- **方法**: `GET`
- **路径**: `/health`
- **描述**: 检查服务健康状态

#### 响应参数

**成功响应** (200):
```json
{"status": "healthy"} 
```
## 配置说明

```bash
# 服务配置
HOST=0.0.0.0
PORT=11433
```