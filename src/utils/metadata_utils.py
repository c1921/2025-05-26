"""
音乐文件元数据提取工具
"""

import os
from typing import Dict, Any, Optional
import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wavpack import WavPack

def extract_metadata(file_path: str) -> Dict[str, Any]:
    """
    从音乐文件中提取元数据
    
    Args:
        file_path: 音乐文件路径
        
    Returns:
        包含元数据的字典
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        # 基本元数据字典
        metadata = {
            "title": None,
            "artist": None,
            "album": None,
            "year": None,
            "track": None,
            "genre": None,
            "duration": None,
            "bitrate": None,
            "sample_rate": None,
        }
        
        # 根据文件类型选择处理方法
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.mp3':
            return extract_mp3_metadata(file_path, metadata)
        elif ext == '.flac':
            return extract_flac_metadata(file_path, metadata)
        elif ext == '.ogg':
            return extract_ogg_metadata(file_path, metadata)
        elif ext == '.wav':
            return extract_wav_metadata(file_path, metadata)
        else:
            # 使用通用方法
            return extract_generic_metadata(file_path, metadata)
            
    except Exception as e:
        print(f"提取元数据时出错: {file_path}, 错误: {str(e)}")
        return {}

def extract_mp3_metadata(file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """提取MP3文件元数据"""
    try:
        audio = MP3(file_path)
        id3 = ID3(file_path)
        
        # 基本音频信息
        metadata["duration"] = int(audio.info.length)
        metadata["bitrate"] = audio.info.bitrate // 1000  # 转换为kbps
        metadata["sample_rate"] = audio.info.sample_rate
        
        # ID3标签
        if 'TIT2' in id3:  # 标题
            metadata["title"] = str(id3['TIT2'])
        if 'TPE1' in id3:  # 艺术家
            metadata["artist"] = str(id3['TPE1'])
        if 'TALB' in id3:  # 专辑
            metadata["album"] = str(id3['TALB'])
        if 'TDRC' in id3:  # 年份
            metadata["year"] = str(id3['TDRC'])
        if 'TRCK' in id3:  # 音轨
            metadata["track"] = str(id3['TRCK'])
        if 'TCON' in id3:  # 流派
            metadata["genre"] = str(id3['TCON'])
        
        return metadata
    except Exception:
        return metadata

def extract_flac_metadata(file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """提取FLAC文件元数据"""
    try:
        audio = FLAC(file_path)
        
        # 基本音频信息
        metadata["duration"] = int(audio.info.length)
        metadata["bitrate"] = int(audio.info.bitrate // 1000)  # 转换为kbps
        metadata["sample_rate"] = audio.info.sample_rate
        
        # FLAC标签
        if 'title' in audio:
            metadata["title"] = str(audio['title'][0]) if audio['title'] else None
        if 'artist' in audio:
            metadata["artist"] = str(audio['artist'][0]) if audio['artist'] else None
        if 'album' in audio:
            metadata["album"] = str(audio['album'][0]) if audio['album'] else None
        if 'date' in audio:
            metadata["year"] = str(audio['date'][0]) if audio['date'] else None
        if 'tracknumber' in audio:
            metadata["track"] = str(audio['tracknumber'][0]) if audio['tracknumber'] else None
        if 'genre' in audio:
            metadata["genre"] = str(audio['genre'][0]) if audio['genre'] else None
        
        return metadata
    except Exception:
        return metadata

def extract_ogg_metadata(file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """提取OGG文件元数据"""
    try:
        audio = OggVorbis(file_path)
        
        # 基本音频信息
        metadata["duration"] = int(audio.info.length)
        metadata["bitrate"] = audio.info.bitrate // 1000  # 转换为kbps
        metadata["sample_rate"] = audio.info.sample_rate
        
        # OGG标签
        if 'title' in audio:
            metadata["title"] = str(audio['title'][0]) if audio['title'] else None
        if 'artist' in audio:
            metadata["artist"] = str(audio['artist'][0]) if audio['artist'] else None
        if 'album' in audio:
            metadata["album"] = str(audio['album'][0]) if audio['album'] else None
        if 'date' in audio:
            metadata["year"] = str(audio['date'][0]) if audio['date'] else None
        if 'tracknumber' in audio:
            metadata["track"] = str(audio['tracknumber'][0]) if audio['tracknumber'] else None
        if 'genre' in audio:
            metadata["genre"] = str(audio['genre'][0]) if audio['genre'] else None
        
        return metadata
    except Exception:
        return metadata

def extract_wav_metadata(file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """提取WAV文件元数据"""
    try:
        audio = mutagen.File(file_path)
        
        # 基本音频信息
        if audio and hasattr(audio.info, 'length'):
            metadata["duration"] = int(audio.info.length)
        if audio and hasattr(audio.info, 'bitrate'):
            metadata["bitrate"] = audio.info.bitrate // 1000 if audio.info.bitrate else None
        if audio and hasattr(audio.info, 'sample_rate'):
            metadata["sample_rate"] = audio.info.sample_rate
        
        return metadata
    except Exception:
        return metadata

def extract_generic_metadata(file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """使用通用方法提取元数据"""
    try:
        audio = mutagen.File(file_path)
        
        if audio:
            # 基本音频信息
            if hasattr(audio.info, 'length'):
                metadata["duration"] = int(audio.info.length)
            if hasattr(audio.info, 'bitrate'):
                metadata["bitrate"] = audio.info.bitrate // 1000 if audio.info.bitrate else None
            if hasattr(audio.info, 'sample_rate'):
                metadata["sample_rate"] = audio.info.sample_rate
            
            # 尝试获取标签
            if hasattr(audio, 'tags') and audio.tags:
                tags = audio.tags
                if 'title' in tags:
                    metadata["title"] = str(tags['title'][0]) if isinstance(tags['title'], list) else str(tags['title'])
                if 'artist' in tags:
                    metadata["artist"] = str(tags['artist'][0]) if isinstance(tags['artist'], list) else str(tags['artist'])
                if 'album' in tags:
                    metadata["album"] = str(tags['album'][0]) if isinstance(tags['album'], list) else str(tags['album'])
        
        return metadata
    except Exception:
        return metadata

def format_duration(seconds: Optional[int]) -> str:
    """
    将秒数格式化为mm:ss格式
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时长字符串
    """
    if seconds is None:
        return "00:00"
    
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}" 