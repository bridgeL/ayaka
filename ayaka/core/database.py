from typing import Optional
import inflection
from loguru import logger
from sqlalchemy.orm import declared_attr
from sqlmodel import MetaData, Session, SQLModel, Field, select, create_engine
from .context import get_context
from ..adapters import get_adapter
from ..helpers import ensure_dir_exists, simple_async_wrap


class AyakaDB:

    def __init__(self, name: str = "ayaka", auto_init: bool = True) -> None:
        self.name = name
        self.metadata = MetaData(info={"name": name})

        class Model(SQLModel):
            metadata = self.metadata

            @declared_attr
            def __tablename__(cls) -> str:
                return inflection.underscore(cls.__name__)

        self.SQLModel = Model

        class DBBase(Model):
            id: Optional[int] = Field(None, primary_key=True)

        self.EasyModel = DBBase

        class GroupDBBase(Model):
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

        self.GroupDBBase = GroupDBBase

        class UserDBBase(GroupDBBase):
            user_id: str = Field(primary_key=True)

            @classmethod
            def get_or_create(cls, group_id: str, user_id: str):
                return cls._get_or_create(group_id=group_id, user_id=user_id)

        self.UserDBBase = UserDBBase

        if auto_init:
            get_adapter().on_startup(simple_async_wrap(self.init))

    def init(self):
        '''初始化所有表'''
        self.path = ensure_dir_exists(f"data/{self.name}/ayaka.db")
        self.engine = create_engine(f"sqlite:///{self.path}")
        self.metadata.bind = self.engine
        self.metadata.create_all()
        logger.opt(colors=True).debug(f"已初始化数据库 <g>{self.name}</g>")

    def get_session(self, **kwargs):
        '''创建一个新的数据库session

        kwargs 请参考sqlmodel.Session'''

        kwargs.setdefault("bind", self.engine)
        # 在数据库高频修改的情况下，autoflush可能会导致数据错误，例如多次相加只生效1次
        # 但减少了数据库崩溃报错的可能，并且提高数据库吞吐量
        kwargs.setdefault("autoflush", False)
        # expire_on_commit 在commit后失效所有orm对象，一般建议关了
        kwargs.setdefault("expire_on_commit", False)

        return Session(**kwargs)


ayaka_db = AyakaDB(auto_init=False)

# 兼容性
get_session = ayaka_db.get_session
GroupDBBase = ayaka_db.GroupDBBase
UserDBBase = ayaka_db.UserDBBase
