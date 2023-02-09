'''上下文'''
import asyncio
from typing import TYPE_CHECKING
from sqlmodel import Session
from contextvars import ContextVar
from ..helpers import simple_repr
from ..adapters import AyakaEvent

if TYPE_CHECKING:
    from .trigger import AyakaTrigger


class UndefinedType:
    pass


Undefined = UndefinedType()
context_dict: dict[str, ContextVar] = {}


class AyakaContextProp(property):

    def __init__(self, context: ContextVar, default_factory) -> None:
        self.context = context
        self.default_factory = default_factory
        super().__init__(self.fget, self.fset, None, None)

    def fget(self, _self):
        try:
            return self.context.get()
        except LookupError as e:
            if self.default_factory:
                s = self.default_factory()
                self.context.set(s)
                return s
            raise e

    def fset(self, _self, v):
        self.context.set(v)


class FieldInfo:
    def __init__(self, default, default_factory, exclude) -> None:
        self.default = default
        self.default_factory = default_factory
        self.exclude = exclude

    def create_prop(self, name: str):
        if self.default is Undefined:
            context = ContextVar(name)
        else:
            context = ContextVar(name, default=self.default)
        return AyakaContextProp(context, self.default_factory)


def Field(default=Undefined, default_factory=None, exclude=False):
    return FieldInfo(default, default_factory, exclude)


def get_db_session():
    ayaka_context.db_session_flag = True
    ayaka_context.wait_tasks = []
    return ayaka_context.trigger.cat.db.get_session()


class AyakaContext:
    '''上下文，保存一些数据便于访问'''

    event: AyakaEvent
    '''消息事件'''

    trigger: "AyakaTrigger"
    '''当前触发器'''

    cmd: str
    '''当前命令'''

    arg: str
    '''去掉命令的剩余文字'''

    args: list[str]
    '''剩余文字根据separate分割'''

    nums: list[int]
    '''数字'''

    wait_tasks: list[asyncio.Task] = []
    '''数据库会话关闭前，会等待该队列中的所有任务结束'''

    db_session: Session = Field(default_factory=get_db_session)
    '''数据库会话，请在trigger存在的时候使用'''

    db_session_flag: bool = False

    def __new__(cls):
        for key in cls.__annotations__.keys():
            name = f"_{key}"

            if hasattr(cls, key):
                value = getattr(cls, key)
                if not isinstance(value, FieldInfo):
                    value = Field(default=value)
            else:
                value = Field()

            if value.exclude:
                continue

            setattr(cls, key, value.create_prop(name))
        return super().__new__(cls)

    def __repr__(self) -> str:
        return simple_repr(self)


ayaka_context = AyakaContext()
