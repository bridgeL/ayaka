from sqlmodel import create_engine, Session, SQLModel
from loguru import logger
from .helpers import ensure_dir_exists

sqlite_path = "data/ayaka/ayaka.db"
sqlite_url = f"sqlite:///{sqlite_path}"


async def create_all():
    '''创建所有表，时间点必须在插件加载之后'''

    # 确保路径存在
    ensure_dir_exists(sqlite_path)

    # 创建引擎
    _engine = create_engine(sqlite_url)

    # 绑定
    SQLModel.metadata.bind = _engine

    # 创建所有表
    SQLModel.metadata.create_all()

    # 日志
    logger.success("数据库已连接")


def get_session(**kwargs):
    '''获取数据库session
    
    kwargs 请参考sqlmodel.Session'''
    
    kwargs.setdefault("bind", SQLModel.metadata.bind)
    # expire_on_commit 在commit后失效所有orm对象，一般建议关了
    kwargs.setdefault("expire_on_commit", False)
    
    return Session(**kwargs)
