from fastapi import APIRouter, HTTPException, BackgroundTasks, Path
from typing import Dict, Any

from src.models.player import player
from src.utils.file_utils import get_file_path, file_exists, decode_filename, get_music_by_id

router = APIRouter(prefix="/api")

@router.post("/play/{file_id}")
async def play_song(file_id: str = Path(..., description="音乐文件ID或文件名"), background_tasks: BackgroundTasks = None):
    """播放指定歌曲"""
    # 获取文件路径
    file_path = get_file_path(file_id)
    
    # 获取音乐信息（如果是ID）
    music_info = get_music_by_id(file_id)
    song_name = music_info["name"] if music_info else decode_filename(file_id)
    
    # 检查文件是否存在
    if not file_exists(file_id):
        raise HTTPException(status_code=404, detail=f"文件不存在: {song_name}")
    
    # 如果正在播放，先停止
    if player.active:
        player.stop()
    
    # 加载并播放文件
    player.load_file(file_path)
    player.play()
    player.current_song = song_name
    
    return {
        "status": "playing",
        "song": song_name,
        "duration": player.duration
    }

@router.post("/pause")
async def pause_song():
    """暂停播放"""
    if not player.active:
        raise HTTPException(status_code=400, detail="没有正在播放的歌曲")
    
    if player.playing:
        player.pause()
        return {"status": "paused"}
    else:
        raise HTTPException(status_code=400, detail="歌曲已经处于暂停状态")

@router.post("/resume")
async def resume_song():
    """恢复播放"""
    if not player.active:
        raise HTTPException(status_code=400, detail="没有正在播放的歌曲")
    
    if player.paused:
        player.resume()
        return {"status": "playing"}
    else:
        raise HTTPException(status_code=400, detail="歌曲已经处于播放状态")

@router.post("/stop")
async def stop_song():
    """停止播放"""
    if not player.active:
        raise HTTPException(status_code=400, detail="没有正在播放的歌曲")
    
    player.stop()
    return {"status": "stopped"}

@router.post("/seek")
async def seek_position(position_data: dict):
    """调整播放位置"""
    if not player.active:
        raise HTTPException(status_code=400, detail="没有正在播放的歌曲")
    
    position = float(position_data.get('position', 0))
    player.seek(position)
    return {"status": "seek", "position": position}

@router.post("/volume")
async def set_volume(volume_data: dict):
    """设置音量"""
    volume = float(volume_data.get('volume', 0))
    if volume < 0 or volume > 1:
        raise HTTPException(status_code=400, detail="音量必须在0-1范围内")
    
    player.set_volume(volume)
    return {"status": "volume_set", "volume": volume}

@router.post("/loop")
async def set_loop(loop_data: dict):
    """设置循环播放"""
    loop = bool(loop_data.get('loop', False))
    player.set_loop(loop)
    return {"status": "loop_set", "loop": loop}

@router.get("/status")
async def get_status():
    """获取当前播放状态"""
    return player.get_status() 