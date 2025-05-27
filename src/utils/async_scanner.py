"""
异步音乐库扫描器
"""

import asyncio
import threading
import time
from typing import List, Dict, Any, Optional, Callable

from src.utils.file_utils import scan_music_library, clear_cache

class AsyncLibraryScanner:
    """异步音乐库扫描器，用于在后台扫描音乐库"""
    
    def __init__(self):
        self.is_scanning = False
        self.last_scan_time = 0
        self.scan_result: Optional[List[Dict[str, Any]]] = None
        self.scan_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable] = []  # 扫描完成后的回调函数列表
    
    def start_scan(self, include_metadata: bool = False) -> bool:
        """
        开始异步扫描
        
        Args:
            include_metadata: 是否包含音乐元数据
            
        Returns:
            是否成功启动扫描
        """
        # 如果已经在扫描中，返回False
        if self.is_scanning:
            return False
        
        # 标记为扫描中
        self.is_scanning = True
        
        # 在新线程中执行扫描
        self.scan_thread = threading.Thread(
            target=self._scan_thread_func,
            args=(include_metadata,),
            daemon=True
        )
        self.scan_thread.start()
        
        return True
    
    def _scan_thread_func(self, include_metadata: bool) -> None:
        """扫描线程函数"""
        try:
            # 强制刷新缓存，执行扫描
            self.scan_result = scan_music_library(force_refresh=True, include_metadata=include_metadata)
            self.last_scan_time = time.time()
            
            # 执行回调
            for callback in self.callbacks:
                try:
                    callback(self.scan_result)
                except Exception as e:
                    print(f"执行扫描回调时出错: {str(e)}")
                    
        except Exception as e:
            print(f"音乐库扫描出错: {str(e)}")
        finally:
            self.is_scanning = False
    
    def register_callback(self, callback: Callable) -> None:
        """
        注册扫描完成后的回调函数
        
        Args:
            callback: 回调函数，接收扫描结果作为参数
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """取消注册回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_status(self) -> Dict[str, Any]:
        """获取扫描状态"""
        return {
            "is_scanning": self.is_scanning,
            "last_scan_time": self.last_scan_time,
            "has_result": self.scan_result is not None
        }


# 创建全局扫描器实例
scanner = AsyncLibraryScanner() 