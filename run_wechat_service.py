import uvicorn
from api.wechat_style_service import app

if __name__ == "__main__":
    uvicorn.run(
        "api.wechat_style_service:app",
        host="0.0.0.0",
        port=11432,
        reload=True
    ) 