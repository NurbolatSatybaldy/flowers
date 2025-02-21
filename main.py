from fastapi import FastAPI
from database import init_tables
from routers.endpoints import router as api_router

app = FastAPI()
init_tables()
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
