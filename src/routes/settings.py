from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import importlib

from src.config.settings_manager import (
    get_music_libraries,
    update_music_libraries,
    load_config,
    save_config
)
import src.config.settings
from src.utils.file_utils import scan_music_library, clear_cache

router = APIRouter(prefix="/settings", tags=["settings"])

class MusicLibraryRequest(BaseModel):
    """音乐库目录列表请求模型"""
    directories: List[str]

class ConfigResponse(BaseModel):
    """配置响应模型"""
    music_library_dirs: List[str]
    supported_formats: List[str]
    api_host: str
    api_port: int
    api_reload: bool

@router.get("/libraries", response_model=List[str])
async def get_libraries():
    """获取所有配置的音乐库目录"""
    return get_music_libraries()

@router.post("/libraries")
async def set_libraries(request: MusicLibraryRequest):
    """设置音乐库目录列表"""
    # 验证路径是否存在
    invalid_paths = []
    for path in request.directories:
        if not os.path.exists(path) or not os.path.isdir(path):
            invalid_paths.append(path)
    
    if invalid_paths:
        return JSONResponse(
            status_code=400,
            content={"error": "以下路径无效或不存在", "invalid_paths": invalid_paths}
        )
    
    # 更新音乐库目录
    success = update_music_libraries(request.directories)
    if not success:
        raise HTTPException(status_code=500, detail="更新配置失败")
    
    # 更新内存中的设置
    src.config.settings.MUSIC_LIBRARY_DIRS = request.directories
    
    # 清除缓存并立即重新扫描音乐库
    clear_cache()
    try:
        # 强制刷新缓存
        file_count = len(scan_music_library(force_refresh=True))
        return {
            "message": "音乐库目录已更新", 
            "directories": request.directories,
            "file_count": file_count
        }
    except Exception as e:
        print(f"重新扫描音乐库时出错: {e}")
        return {
            "message": "音乐库目录已更新，但扫描过程中出现错误", 
            "directories": request.directories,
            "error": str(e)
        }

@router.post("/refresh-library")
async def refresh_music_library():
    """强制刷新音乐库缓存"""
    try:
        # 确保从配置文件中重新读取最新的音乐库目录
        src.config.settings.MUSIC_LIBRARY_DIRS = get_music_libraries()
        
        # 清除缓存
        clear_cache()
        # 强制重新扫描
        file_count = len(scan_music_library(force_refresh=True))
        return {
            "success": True,
            "message": f"音乐库已刷新，共找到 {file_count} 个音乐文件",
            "file_count": file_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新音乐库失败: {str(e)}")

@router.get("/config", response_model=ConfigResponse)
async def get_full_config():
    """获取完整配置"""
    config = load_config()
    return config

@router.put("/config")
async def update_full_config(config: Dict[str, Any]):
    """更新完整配置"""
    success = save_config(config)
    if not success:
        raise HTTPException(status_code=500, detail="更新配置失败")
    
    # 动态重新加载设置
    if "music_library_dirs" in config:
        src.config.settings.MUSIC_LIBRARY_DIRS = config["music_library_dirs"]
        
        # 清除缓存并重新扫描音乐库
        clear_cache()
        try:
            file_count = len(scan_music_library(force_refresh=True))
            print(f"配置更新后重新扫描音乐库，共找到 {file_count} 个文件")
        except Exception as e:
            print(f"重新扫描音乐库时出错: {e}")
    
    if "supported_formats" in config:
        src.config.settings.SUPPORTED_FORMATS = config["supported_formats"]
    
    if "api_host" in config:
        src.config.settings.API_HOST = config["api_host"]
    
    if "api_port" in config:
        src.config.settings.API_PORT = config["api_port"]
    
    if "api_reload" in config:
        src.config.settings.API_RELOAD = config["api_reload"]
    
    return {"message": "配置已更新"} 