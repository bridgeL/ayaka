from loguru import logger
from sqlmodel import create_engine, SQLModel, Session
from .bridge import bridge
from .helpers import ensure_dir_exists

sqlite_path = "data/ayaka/ayaka.db"
ensure_dir_exists(sqlite_path)
sqlite_url = f"sqlite:///{sqlite_path}"
engine = create_engine(sqlite_url)


@bridge.on_startup
async def orm_init():
    SQLModel.metadata.create_all(engine)
    logger.info("数据库已连接")


def get_session(**kwargs):
    # expire_on_commit 在commit后失效所有orm对象，一般建议关了
    kwargs.setdefault("expire_on_commit", False)
    return Session(engine, **kwargs)
