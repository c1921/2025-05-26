from fastapi import APIRouter
from typing import List, Dict, Any

from src.utils.file_utils import get_all_music_files

router = APIRouter(prefix="/api")

@router.get("/songs", response_model=List[Dict[str, Any]])
async def get_songs():
    """获取所有歌曲列表"""
    return get_all_music_files() 