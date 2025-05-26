import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config.settings import MUSIC_DIR, API_HOST, API_PORT, API_RELOAD
from src.routes import api_router

# 创建FastAPI应用
app = FastAPI(title="音乐播放器API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 挂载静态文件目录
app.mount("/music", StaticFiles(directory=MUSIC_DIR), name="music")

# 包含API路由
app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "音乐播放器API运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=API_HOST, port=API_PORT, reload=API_RELOAD) 