import uvicorn
from api.description_api_serve import app

if __name__ == "__main__":
    uvicorn.run(
        "api.description_api_serve:app",
        host="0.0.0.0",
        port=11431,
        reload=True
    ) 