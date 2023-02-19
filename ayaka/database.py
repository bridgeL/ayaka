from ayaka_db import AyakaDB as BaseAyakaDB
from sqlmodel import Field
from .context import ayaka_context


class AyakaDB(BaseAyakaDB):
    '''数据库'''

    def __init__(self, name: str = "ayaka") -> None:
        super().__init__(name)

        Model = self.Model

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


db_dict: dict[str, AyakaDB] = {}


def get_db(name: str = "ayaka"):
    '''获取对应名称的数据库，不存在则自动新建'''
    if name not in db_dict:
        db_dict[name] = AyakaDB(name)
    return db_dict[name]
