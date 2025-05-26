import os
import json
from typing import List, Dict, Any

# 默认配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")

# 默认配置
DEFAULT_CONFIG = {
    "music_library_dirs": [],
    "supported_formats": ['.mp3', '.wav', '.ogg', '.flac'],
    "api_host": "0.0.0.0",
    "api_port": 8000,
    "api_reload": True
}

def load_config() -> Dict[str, Any]:
    """从JSON文件加载配置，如果不存在则创建默认配置文件"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保所有必要的配置项都存在
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception as e:
        print(f"加载配置出错: {e}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> bool:
    """保存配置到JSON文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存配置出错: {e}")
        return False

def update_music_libraries(library_dirs: List[str]) -> bool:
    """更新音乐库目录列表"""
    config = load_config()
    config["music_library_dirs"] = library_dirs
    return save_config(config)

def get_music_libraries() -> List[str]:
    """获取音乐库目录列表"""
    config = load_config()
    return config.get("music_library_dirs", [])

def get_config_value(key: str, default=None):
    """获取指定配置项的值"""
    config = load_config()
    return config.get(key, default) 