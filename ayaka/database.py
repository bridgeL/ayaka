from loguru import logger
from sqlmodel import create_engine, SQLModel, Session
from .helpers import ensure_dir_exists

sqlite_path = "data/ayaka/ayaka.db"
sqlite_url = f"sqlite:///{sqlite_path}"
_engine = None


async def create_all():
    '''创建所有表，时间点必须在插件加载之后'''
    global _engine

    # 确保路径存在
    ensure_dir_exists(sqlite_path)

    # 创建引擎
    _engine = create_engine(sqlite_url)

    # 创建所有表
    SQLModel.metadata.create_all(_engine)
    logger.success("数据库已连接")


def get_session(**kwargs):
    '''kwargs请参考sqlmodel.Session'''
    # expire_on_commit 在commit后失效所有orm对象，一般建议关了
    kwargs.setdefault("expire_on_commit", False)
    return Session(_engine, **kwargs)
