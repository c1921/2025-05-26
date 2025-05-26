import os
from src.config.settings_manager import get_music_libraries, get_config_value

# 应用程序基本路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 动态获取音乐库目录
def get_current_music_libraries():
    return get_music_libraries()

# 音乐库目录列表
MUSIC_LIBRARY_DIRS = get_current_music_libraries()

# 支持的音频格式
SUPPORTED_FORMATS = get_config_value("supported_formats", ['.mp3', '.wav', '.ogg', '.flac'])

# API设置
API_HOST = get_config_value("api_host", "0.0.0.0")
API_PORT = get_config_value("api_port", 8000)
API_RELOAD = get_config_value("api_reload", True) 