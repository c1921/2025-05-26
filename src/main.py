import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

from src.config.settings import API_HOST, API_PORT, API_RELOAD, get_current_music_libraries
from src.routes import api_router
from src.utils.file_utils import decode_filename

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

# 为每个外部音乐库添加路由
@app.get("/library/{library_name}/{path:path}")
async def get_library_file(library_name: str, path: str):
    """访问外部音乐库中的文件"""
    # URL解码
    library_name = decode_filename(library_name)
    path = decode_filename(path)
    
    # 获取最新的音乐库目录列表
    music_library_dirs = get_current_music_libraries()
    
    # 查找匹配的音乐库目录
    for lib_dir in music_library_dirs:
        if os.path.basename(lib_dir) == library_name:
            file_path = os.path.join(lib_dir, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
    
    # 未找到文件
    raise HTTPException(status_code=404, detail="文件未找到")

# 包含API路由
app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "音乐播放器API运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=API_HOST, port=API_PORT, reload=API_RELOAD) 