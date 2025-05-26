import os
import urllib.parse
import hashlib
import time
from typing import List, Dict, Any, Optional
from src.config.settings import SUPPORTED_FORMATS
from src.config.settings_manager import get_music_libraries

# 音乐库扫描结果缓存
_music_files_cache: Optional[List[Dict[str, Any]]] = None
_cache_timestamp: float = 0
_cache_library_dirs: List[str] = []
_CACHE_VALID_TIME = 60  # 缓存有效期（秒）

def scan_music_library(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    扫描所有配置的音乐库目录，获取音乐文件信息
    
    Args:
        force_refresh: 是否强制刷新缓存
    """
    global _music_files_cache, _cache_timestamp, _cache_library_dirs
    
    # 检查缓存是否有效
    current_time = time.time()
    
    # 每次从配置文件获取最新的音乐库目录
    current_library_dirs = get_music_libraries()
    library_dirs_changed = set(current_library_dirs) != set(_cache_library_dirs)
    
    if not force_refresh and _music_files_cache is not None and \
       current_time - _cache_timestamp < _CACHE_VALID_TIME and \
       not library_dirs_changed:
        return _music_files_cache
    
    music_files = []
    file_paths = set()  # 用于去重
    
    # 扫描外部音乐库目录
    for library_dir in current_library_dirs:
        if not os.path.exists(library_dir) or not os.path.isdir(library_dir):
            continue
            
        for root, _, files in os.walk(library_dir):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in SUPPORTED_FORMATS):
                    file_path = os.path.join(root, file)
                    
                    # 如果文件已经在列表中，跳过
                    if file_path in file_paths:
                        continue
                        
                    file_paths.add(file_path)
                    
                    # 计算文件大小（MB）
                    size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
                    
                    # 生成唯一ID
                    file_id = generate_file_id(file_path)
                    
                    # 计算相对路径，用于API访问
                    relative_path = os.path.relpath(file_path, library_dir)
                    encoded_path = '/'.join([urllib.parse.quote(part) for part in relative_path.split(os.sep)])
                    
                    music_files.append({
                        "id": file_id,
                        "name": file,
                        "path": f"/library/{urllib.parse.quote(os.path.basename(library_dir))}/{encoded_path}",
                        "size": size_mb,
                        "add_time": os.path.getctime(file_path),
                        "source": "library",
                        "full_path": file_path
                    })
    
    # 按添加时间排序
    music_files.sort(key=lambda x: x["add_time"], reverse=True)
    
    # 更新缓存
    _music_files_cache = music_files
    _cache_timestamp = current_time
    _cache_library_dirs = current_library_dirs.copy()
    
    return music_files

def get_all_music_files() -> List[Dict[str, Any]]:
    """获取所有音乐文件列表"""
    return scan_music_library()

def clear_cache():
    """清除音乐库扫描缓存"""
    global _music_files_cache, _cache_timestamp
    _music_files_cache = None
    _cache_timestamp = 0

def generate_file_id(file_path: str) -> str:
    """根据文件路径生成唯一ID"""
    return hashlib.md5(file_path.encode('utf-8')).hexdigest()

def decode_filename(filename: str) -> str:
    """解码URL编码的文件名"""
    return urllib.parse.unquote(filename)

def is_supported_format(filename: str) -> bool:
    """检查文件是否是支持的音频格式"""
    # 先解码文件名
    decoded_filename = decode_filename(filename)
    return any(decoded_filename.lower().endswith(fmt) for fmt in SUPPORTED_FORMATS)

def get_file_path(file_id_or_path: str) -> str:
    """
    获取完整的文件路径
    
    可以接受以下格式：
    1. 文件ID - 从音乐库中查找对应的文件
    2. 完整路径 - 直接返回
    """
    # 检查是否是ID格式（32位十六进制字符串）
    if len(file_id_or_path) == 32 and all(c in '0123456789abcdef' for c in file_id_or_path.lower()):
        # 查找对应ID的文件
        music_files = scan_music_library()
        for file in music_files:
            if file["id"] == file_id_or_path:
                return file["full_path"]
    
    # 检查是否是完整路径
    if os.path.exists(file_id_or_path) and os.path.isfile(file_id_or_path):
        return file_id_or_path
    
    # 默认返回解码后的路径（可能不存在）
    return decode_filename(file_id_or_path)

def file_exists(file_id_or_path: str) -> bool:
    """检查文件是否存在"""
    file_path = get_file_path(file_id_or_path)
    return os.path.exists(file_path) and os.path.isfile(file_path)

def get_music_by_id(file_id: str) -> Dict[str, Any]:
    """根据ID获取音乐文件信息"""
    music_files = scan_music_library()
    for file in music_files:
        if file["id"] == file_id:
            return file
    return None 