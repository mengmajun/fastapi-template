import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 功能：在应用服务启动之前初始化数据库
# 场景：应用服务启动时需要初始化数据库，确保数据库表存在并与模型同步
# 注意：如果数据库表不存在，会根据模型自动创建；如果数据库表存在但与模型不一致，会根据模型更新数据库表
# 代码位置：在应用服务启动之前调用 init_db 函数
# 调用时机：应用服务启动时
# 调用频率：每次应用服务启动时

def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
