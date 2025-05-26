import os
from typing import List, Dict, Any
from src.config.settings import MUSIC_DIR, SUPPORTED_FORMATS

def get_all_music_files() -> List[Dict[str, Any]]:
    """获取所有音乐文件列表"""
    music_files = []
    
    for file in os.listdir(MUSIC_DIR):
        file_path = os.path.join(MUSIC_DIR, file)
        if os.path.isfile(file_path) and any(file.lower().endswith(fmt) for fmt in SUPPORTED_FORMATS):
            # 计算文件大小（MB）
            size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
            music_files.append({
                "id": len(music_files),
                "name": file,
                "path": f"/music/{file}",
                "size": size_mb,
                "add_time": os.path.getctime(file_path)
            })
    
    # 按添加时间排序
    music_files.sort(key=lambda x: x["add_time"], reverse=True)
    return music_files

def is_supported_format(filename: str) -> bool:
    """检查文件是否是支持的音频格式"""
    return any(filename.lower().endswith(fmt) for fmt in SUPPORTED_FORMATS)

def get_file_path(filename: str) -> str:
    """获取完整的文件路径"""
    return os.path.join(MUSIC_DIR, filename)

def file_exists(filename: str) -> bool:
    """检查文件是否存在"""
    file_path = get_file_path(filename)
    return os.path.exists(file_path) and os.path.isfile(file_path) 