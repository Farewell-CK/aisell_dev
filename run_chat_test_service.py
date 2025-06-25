import uvicorn
from api.chat_test_service import app

if __name__ == "__main__":
    uvicorn.run(
        "api.chat_test_service:app",
        host="0.0.0.0",
        port=11433,
        reload=True,
        workers=4  # 设置工作进程数，根据CPU核心数调整
    ) 