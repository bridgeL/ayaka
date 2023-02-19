import inflection
from pathlib import Path
from typing import Optional
from loguru import logger
from sqlalchemy.orm import declared_attr
from sqlalchemy.future import Engine
from sqlmodel import MetaData, Session, SQLModel, Field, select, create_engine
from ayaka_utils import ensure_dir_exists
from .context import ayaka_context


class AyakaDB:
    '''数据库'''

    def __init__(self, name: str = "ayaka") -> None:
        self.name = name
        db_dict[name] = self

        self.metadata = MetaData(info={"name": name})
        self.path: Path = None
        self.engine: Engine = None

        class Model(SQLModel):
            metadata = self.metadata

            @declared_attr
            def __tablename__(cls) -> str:
                return inflection.underscore(cls.__name__)

            @staticmethod
            def get_session(**kwargs):
                '''创建一个新的数据库session

                kwargs 请参考sqlmodel.Session'''
                return self.get_session(**kwargs)

            @classmethod
            def _get_or_create(cls, session: Session, **kwargs):
                '''若不存在则根据参数值创建'''
                statement = select(cls).filter_by(**kwargs)
                cursor = session.exec(statement)
                data = cursor.one_or_none()
                if not data:
                    data = cls(**kwargs)
                    session.add(data)
                return data
        self.Model = Model
        '''基本模型'''

        class IDModel(Model):
            id: Optional[int] = Field(None, primary_key=True)
        self.IDModel = IDModel
        '''自带id的基本模型'''

        class GroupDBBase(Model):
            group_id: str = Field(primary_key=True)

            @classmethod
            def get_or_create(cls, group_id: str):
                return cls._get_or_create(
                    ayaka_context.db_session,
                    group_id=group_id
                )
        self.GroupDBBase = GroupDBBase
        '''自带group_id的基本模型'''

        class UserDBBase(Model):
            group_id: str = Field(primary_key=True)
            user_id: str = Field(primary_key=True)

            @classmethod
            def get_or_create(cls, group_id: str, user_id: str):
                return cls._get_or_create(
                    ayaka_context.db_session,
                    group_id=group_id,
                    user_id=user_id
                )
        self.UserDBBase = UserDBBase
        '''自带group_id、user_id的基本模型'''

    def init(self):
        '''初始化所有表'''
        if self.path:
            logger.opt(colors=True).warning(
                f"你正试图重复初始化数据库 <g>{self.path}</g>，已取消该操作，请确保你的代码符合预期")
            return
        self.path = ensure_dir_exists(f"data/{self.name}/data.db")
        self.engine = create_engine(f"sqlite:///{self.path}")
        self.metadata.bind = self.engine
        self.metadata.create_all()
        logger.opt(colors=True).debug(f"已初始化数据库 <g>{self.path}</g>")

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


db_dict: dict[str, AyakaDB] = {}


def get_db(name: str = "ayaka"):
    '''获取对应名称的数据库，不存在则自动新建'''
    if name not in db_dict:
        db_dict[name] = AyakaDB(name)
    return db_dict[name]
