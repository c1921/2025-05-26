from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Dict, Any, Optional
import os

from src.utils.file_utils import get_all_music_files, get_file_path, file_exists
from src.utils.metadata_utils import extract_metadata
from src.utils.search_utils import search_music, filter_music

router = APIRouter(prefix="/api")

@router.get("/songs", response_model=List[Dict[str, Any]])
async def get_songs(
    include_metadata: bool = Query(False, description="是否包含音乐元数据")
):
    """获取所有歌曲列表"""
    return get_all_music_files(include_metadata=include_metadata)

@router.get("/songs/{file_id}/metadata", response_model=Dict[str, Any])
async def get_song_metadata(
    file_id: str = Path(..., description="音乐文件ID")
):
    """获取指定歌曲的元数据"""
    file_path = get_file_path(file_id)
    
    if not file_exists(file_id):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 提取文件名作为默认标题
    file_name = os.path.basename(file_path)
    title = os.path.splitext(file_name)[0]
    
    # 提取元数据
    metadata = extract_metadata(file_path)
    
    # 基本信息
    result = {
        "id": file_id,
        "name": file_name,
        "title": metadata.get("title") or title,
        "metadata": metadata
    }
    
    return result

@router.get("/songs/search", response_model=Dict[str, Any])
async def search_songs(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(50, description="最大返回结果数量", ge=1, le=200),
    artist: Optional[str] = Query(None, description="按艺术家筛选"),
    album: Optional[str] = Query(None, description="按专辑筛选"),
    genre: Optional[str] = Query(None, description="按流派筛选"),
    min_duration: Optional[int] = Query(None, description="最小时长（秒）", ge=0),
    max_duration: Optional[int] = Query(None, description="最大时长（秒）", ge=0),
):
    """
    搜索歌曲
    
    返回:
        - items: 搜索结果列表
        - total: 结果总数
        - query: 搜索关键词
    """
    # 搜索音乐
    search_results = search_music(q, include_metadata=True, limit=limit)
    
    # 应用筛选
    if any([artist, album, genre, min_duration, max_duration]):
        filtered_results = filter_music(
            search_results,
            artist=artist,
            album=album,
            genre=genre,
            min_duration=min_duration,
            max_duration=max_duration
        )
    else:
        filtered_results = search_results
    
    return {
        "items": filtered_results,
        "total": len(filtered_results),
        "query": q
    } 