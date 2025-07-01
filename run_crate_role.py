import uvicorn
from api.create_role_service import app

if __name__ == "__main__":
    uvicorn.run(
        "api.create_role_service:app",
        host="0.0.0.0",
        port=11435,
        reload=True
    )