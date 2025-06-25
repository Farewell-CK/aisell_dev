import uvicorn
# from api.opening_service import app

if __name__ == "__main__":
    uvicorn.run(
        "api.opening_service:app",
        host="0.0.0.0",
        port=11434,
        reload=True,
        log_level="info"
    ) 