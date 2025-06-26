#!/usr/bin/env python3
"""
异步文档总结API服务启动脚本
"""

import uvicorn
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from api.description_api_serve import app

if __name__ == "__main__":
    # 配置服务器参数
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 11431))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"启动异步文档总结API服务...")
    print(f"服务地址: http://{host}:{port}")
    print(f"自动重载: {reload}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"API文档(ReDoc): http://{host}:{port}/redoc")
    
    # 启动服务器
    uvicorn.run(
        "api.description_api_serve:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 