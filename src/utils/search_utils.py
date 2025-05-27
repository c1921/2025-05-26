"""
音乐搜索工具
"""

from typing import List, Dict, Any, Optional
import re

from src.utils.file_utils import get_all_music_files

def search_music(query: str, include_metadata: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
    """
    搜索音乐文件
    
    Args:
        query: 搜索关键词
        include_metadata: 是否包含元数据
        limit: 最大返回结果数量
        
    Returns:
        匹配的音乐文件列表
    """
    if not query or not query.strip():
        return []
    
    # 规范化查询字符串
    query = query.lower().strip()
    
    # 获取所有音乐文件（包含元数据）
    all_files = get_all_music_files(include_metadata=include_metadata)
    
    # 存储搜索结果和评分
    search_results = []
    
    for file in all_files:
        score = 0
        match_reasons = []
        
        # 文件名匹配
        if query in file["name"].lower():
            score += 10
            match_reasons.append("文件名匹配")
        
        # 如果有元数据信息，检查元数据
        if "metadata" in file:
            metadata = file["metadata"]
            
            # 标题匹配
            if metadata.get("title") and query in metadata["title"].lower():
                score += 15
                match_reasons.append("标题匹配")
            
            # 艺术家匹配
            if metadata.get("artist") and query in metadata["artist"].lower():
                score += 12
                match_reasons.append("艺术家匹配")
            
            # 专辑匹配
            if metadata.get("album") and query in metadata["album"].lower():
                score += 8
                match_reasons.append("专辑匹配")
            
            # 流派匹配
            if metadata.get("genre") and query in metadata["genre"].lower():
                score += 5
                match_reasons.append("流派匹配")
        
        # 如果有匹配，添加到结果中
        if score > 0:
            result = file.copy()
            result["score"] = score
            result["match_reasons"] = match_reasons
            search_results.append(result)
    
    # 按评分排序
    search_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 限制返回数量
    return search_results[:limit]

def filter_music(
    files: List[Dict[str, Any]],
    artist: Optional[str] = None,
    album: Optional[str] = None,
    genre: Optional[str] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    筛选音乐文件
    
    Args:
        files: 要筛选的音乐文件列表
        artist: 艺术家
        album: 专辑
        genre: 流派
        min_duration: 最小时长（秒）
        max_duration: 最大时长（秒）
        
    Returns:
        筛选后的音乐文件列表
    """
    filtered = files.copy()
    
    # 按艺术家筛选
    if artist:
        artist = artist.lower()
        filtered = [
            f for f in filtered 
            if "metadata" in f and f["metadata"].get("artist") and 
            artist in f["metadata"]["artist"].lower()
        ]
    
    # 按专辑筛选
    if album:
        album = album.lower()
        filtered = [
            f for f in filtered 
            if "metadata" in f and f["metadata"].get("album") and 
            album in f["metadata"]["album"].lower()
        ]
    
    # 按流派筛选
    if genre:
        genre = genre.lower()
        filtered = [
            f for f in filtered 
            if "metadata" in f and f["metadata"].get("genre") and 
            genre in f["metadata"]["genre"].lower()
        ]
    
    # 按时长筛选
    if min_duration is not None:
        filtered = [
            f for f in filtered 
            if "metadata" in f and f["metadata"].get("duration") and 
            f["metadata"]["duration"] >= min_duration
        ]
    
    if max_duration is not None:
        filtered = [
            f for f in filtered 
            if "metadata" in f and f["metadata"].get("duration") and 
            f["metadata"]["duration"] <= max_duration
        ]
    
    return filtered 