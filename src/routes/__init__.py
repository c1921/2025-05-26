# 使routes成为一个Python包

from fastapi import APIRouter
from src.routes.songs import router as songs_router
from src.routes.playback import router as playback_router

# 创建主路由
api_router = APIRouter()

# 包含子路由
api_router.include_router(songs_router)
api_router.include_router(playback_router) 