import os

# 应用程序基本路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 音乐存储目录
MUSIC_DIR = os.path.join(BASE_DIR, "music")
os.makedirs(MUSIC_DIR, exist_ok=True)

# 支持的音频格式
SUPPORTED_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']

# API设置
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True 