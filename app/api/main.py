from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)

# 本地环境下，添加私有路由
# 私有路由可以创建用户
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
