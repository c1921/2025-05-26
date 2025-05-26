from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import os
import aiofiles

from src.utils.file_utils import get_all_music_files, is_supported_format, get_file_path, file_exists
from src.models.player import player

router = APIRouter(prefix="/api")

@router.get("/songs", response_model=List[Dict[str, Any]])
async def get_songs():
    """获取所有歌曲列表"""
    return get_all_music_files()

@router.post("/upload")
async def upload_song(file: UploadFile = File(...)):
    """上传歌曲文件"""
    # 检查文件扩展名
    filename = file.filename
    if not is_supported_format(filename):
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 保存文件
    file_path = get_file_path(filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        # 读取上传的文件内容并写入
        content = await file.read()
        await out_file.write(content)
    
    return {"filename": filename, "status": "success"}

@router.delete("/songs/{filename}")
async def delete_song(filename: str):
    """删除歌曲"""
    file_path = get_file_path(filename)
    
    # 检查文件是否存在
    if not file_exists(filename):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 如果正在播放此文件，先停止播放
    if player.current_song == filename and player.active:
        player.stop()
    
    # 删除文件
    os.remove(file_path)
    return {"filename": filename, "status": "deleted"} 