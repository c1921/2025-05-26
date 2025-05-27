from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
import os
from typing import List, Dict, Any

from src.config.settings import get_current_music_libraries
from src.utils.file_utils import decode_filename, clear_cache
from src.config.settings_manager import get_music_libraries, update_music_libraries
from src.utils.async_scanner import scanner

router = APIRouter(prefix="/api")

@router.get("/library", response_model=Dict[str, Any])
async def get_library_info():
    """获取音乐库信息"""
    libraries = get_music_libraries()
    return {
        "libraries": libraries,
        "count": len(libraries)
    }

@router.post("/library", response_model=Dict[str, Any])
async def update_library(library_data: Dict[str, List[str]]):
    """更新音乐库目录"""
    if "libraries" not in library_data:
        raise HTTPException(status_code=400, detail="缺少libraries字段")
    
    # 验证目录列表
    libraries = library_data["libraries"]
    if not isinstance(libraries, list):
        raise HTTPException(status_code=400, detail="libraries必须是一个数组")
    
    # 更新音乐库目录
    success = update_music_libraries(libraries)
    if not success:
        raise HTTPException(status_code=500, detail="更新音乐库目录失败")
    
    # 清除扫描缓存
    clear_cache()
    
    return {
        "success": True,
        "libraries": libraries,
        "count": len(libraries)
    }

@router.post("/library/scan", response_model=Dict[str, Any])
async def scan_library(
    include_metadata: bool = Query(False, description="是否包含音乐元数据")
):
    """开始异步扫描音乐库"""
    # 使用异步扫描器开始扫描
    success = scanner.start_scan(include_metadata=include_metadata)
    
    if not success:
        return {
            "success": False,
            "message": "扫描已在进行中",
            "status": scanner.get_status()
        }
    
    return {
        "success": True,
        "message": "开始扫描音乐库",
        "status": scanner.get_status()
    }

@router.get("/library/scan/status", response_model=Dict[str, Any])
async def get_scan_status():
    """获取音乐库扫描状态"""
    return scanner.get_status()

@router.post("/library/clear-cache", response_model=Dict[str, Any])
async def clear_library_cache():
    """清除音乐库扫描缓存"""
    clear_cache()
    return {"success": True, "message": "缓存已清除"}

@router.get("/library/{library_name}/{path:path}")
async def get_library_file(library_name: str, path: str):
    """提供对外部音乐库文件的访问"""
    # 解码库名和路径
    decoded_library = decode_filename(library_name)
    decoded_path = decode_filename(path)
    
    # 获取最新的音乐库目录列表
    music_library_dirs = get_current_music_libraries()
    
    # 查找匹配的库目录
    matching_library = None
    for library_dir in music_library_dirs:
        if os.path.basename(library_dir) == decoded_library:
            matching_library = library_dir
            break
    
    if not matching_library:
        raise HTTPException(status_code=404, detail=f"未找到音乐库: {decoded_library}")
    
    # 构建完整文件路径
    file_path = os.path.join(matching_library, decoded_path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {decoded_path}")
    
    # 返回文件
    return FileResponse(file_path) 