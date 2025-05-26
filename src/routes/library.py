from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from typing import List

from src.config.settings import get_current_music_libraries
from src.utils.file_utils import decode_filename

router = APIRouter()

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