from loguru import logger
from sqlmodel import create_engine, SQLModel, Session
from .helpers import ensure_dir_exists
from .adapters import get_adapter

sqlite_path = "data/ayaka/ayaka.db"
ensure_dir_exists(sqlite_path)
sqlite_url = f"sqlite:///{sqlite_path}"
engine = create_engine(sqlite_url)


async def orm_init():
    SQLModel.metadata.create_all(engine)
    logger.success("数据库已连接")

get_adapter().on_startup(orm_init)


def get_session(**kwargs):
    '''kwargs请参考sqlmodel.Session'''
    # expire_on_commit 在commit后失效所有orm对象，一般建议关了
    kwargs.setdefault("expire_on_commit", False)
    return Session(engine, **kwargs)
