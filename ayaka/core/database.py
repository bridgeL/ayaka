from loguru import logger
from sqlmodel import create_engine, Session, SQLModel, Field, select
from .context import get_context
from ..helpers import ensure_dir_exists

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
    '''创建一个新的数据库session

    kwargs 请参考sqlmodel.Session'''

    kwargs.setdefault("bind", SQLModel.metadata.bind)
    # 在数据库高频修改的情况下，autoflush可能会导致数据错误，例如多次相加只生效1次
    # 但减少了数据库崩溃报错的可能，并且提高数据库吞吐量
    kwargs.setdefault("autoflush", False)
    # expire_on_commit 在commit后失效所有orm对象，一般建议关了
    kwargs.setdefault("expire_on_commit", False)

    return Session(**kwargs)


class GroupDBBase(SQLModel):
    group_id: str = Field(primary_key=True)

    @classmethod
    def _get_or_create(model, **kwargs):
        session = get_context().db_session
        statement = select(model).filter_by(**kwargs)
        cursor = session.exec(statement)
        instance = cursor.one_or_none()
        if not instance:
            instance = model(**kwargs)
            session.add(instance)
        return instance

    @classmethod
    def get_or_create(cls, group_id: str):
        return cls._get_or_create(group_id=group_id)


class UserDBBase(GroupDBBase):
    user_id: str = Field(primary_key=True)

    @classmethod
    def get_or_create(cls, group_id: str, user_id: str):
        return cls._get_or_create(group_id=group_id, user_id=user_id)
