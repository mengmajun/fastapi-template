from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User

# 在需要认证的接口中通过 Depends(reusable_oauth2) 依赖注入使用
# 该对象会自动从请求header中的 Authorization 头中提取 Bearer 令牌（格式： Bearer <token>
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Annotated 类型注释工具
# 用于给参数添加注释，第一个参数是参数类型，第二个参数是参数来源
# 表示数据库会话依赖 在 FastAPI 处理请求时， Depends(get_db) 会调用 get_db 函数，获取一个数据库会话，并将其注入到需要 SessionDep 的函数中
SessionDep = Annotated[Session, Depends(get_db)]  
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # 从数据库中根据token_data.sub 用户id 查询用户，用户的访问token中编码了用户id，sub表示编码的主题
    # get方法会根据主键查询用户，主键就是用户id 
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
