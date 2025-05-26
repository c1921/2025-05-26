from just_playback import Playback
from typing import Optional

class MusicPlayer:
    """音乐播放器模型类，封装了just_playback库的功能"""
    
    def __init__(self):
        self.playback = Playback()
        self.current_song: Optional[str] = None
        self.playlist = []
        self.is_playing = False
    
    def load_file(self, file_path: str) -> None:
        """加载音乐文件"""
        self.playback.load_file(file_path)
    
    def play(self) -> None:
        """播放当前加载的文件"""
        self.playback.play()
        self.is_playing = True
    
    def pause(self) -> None:
        """暂停播放"""
        if self.playback.playing:
            self.playback.pause()
            self.is_playing = False
    
    def resume(self) -> None:
        """恢复播放"""
        if self.playback.paused:
            self.playback.resume()
            self.is_playing = True
    
    def stop(self) -> None:
        """停止播放"""
        if self.playback.active:
            self.playback.stop()
            self.is_playing = False
            self.current_song = None
    
    def seek(self, position: float) -> None:
        """调整播放位置"""
        if self.playback.active:
            self.playback.seek(position)
    
    def set_volume(self, volume: float) -> None:
        """设置音量"""
        self.playback.set_volume(volume)
    
    def set_loop(self, loop: bool) -> None:
        """设置循环播放"""
        self.playback.loop_at_end(loop)
    
    @property
    def active(self) -> bool:
        """播放器是否处于活动状态"""
        return self.playback.active
    
    @property
    def playing(self) -> bool:
        """是否正在播放"""
        return self.playback.playing
    
    @property
    def paused(self) -> bool:
        """是否暂停"""
        return self.playback.paused
    
    @property
    def position(self) -> float:
        """当前播放位置"""
        return self.playback.curr_pos
    
    @property
    def duration(self) -> float:
        """音频文件长度"""
        return self.playback.duration
    
    @property
    def volume(self) -> float:
        """当前音量"""
        return self.playback.volume
    
    @property
    def loops_at_end(self) -> bool:
        """是否循环播放"""
        return self.playback.loops_at_end
    
    def get_status(self) -> dict:
        """获取当前播放状态"""
        if not self.active:
            return {
                "active": False,
                "playing": False,
                "current_song": None,
                "position": 0,
                "duration": 0,
                "volume": self.volume,
                "loop": self.loops_at_end
            }
        
        return {
            "active": True,
            "playing": self.playing,
            "current_song": self.current_song,
            "position": self.position,
            "duration": self.duration,
            "volume": self.volume,
            "loop": self.loops_at_end
        }

# 创建全局播放器实例
player = MusicPlayer() 