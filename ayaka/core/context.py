'''上下文'''
import asyncio
from typing import TYPE_CHECKING
from sqlmodel import Session
from contextvars import ContextVar
from ..helpers import simple_repr
from ..adapters import AyakaEvent

if TYPE_CHECKING:
    from .trigger import AyakaTrigger

context_dict: dict[str, ContextVar] = {}


class UndefinedType:
    pass


Undefined = UndefinedType()


class AyakaContextProp(property):

    def __init__(self, name: str, default=Undefined, default_factory=None) -> None:
        if default is Undefined:
            self.context = ContextVar(name)
        else:
            self.context = ContextVar(name, default=default)
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
    def __init__(self, default, default_factory) -> None:
        self.default = default
        self.default_factory = default_factory

    def get_prop(self, name: str):
        return AyakaContextProp(name, default=self.default, default_factory=self.default_factory)


def Field(default=Undefined, default_factory=None):
    return FieldInfo(default, default_factory)


def get_db_session():
    return ayaka_context.trigger.cat.db.get_session()


class AyakaContext:
    '''上下文，保存一些数据便于访问'''

    event: AyakaEvent
    trigger: "AyakaTrigger"
    cmd: str
    arg: str
    args: list[str]
    nums: list[int]
    wait_tasks: list[asyncio.Task] = []
    db_session: Session = Field(default_factory=get_db_session)

    def __new__(cls):
        for key in cls.__annotations__.keys():
            name = f"_{key}"

            if hasattr(cls, key):
                value = getattr(cls, key)
                if not isinstance(value, FieldInfo):
                    value = Field(default=value)
            else:
                value = Field()

            setattr(cls, key, value.get_prop(name))
        return super().__new__(cls)

    def __repr__(self) -> str:
        return simple_repr(self)


ayaka_context = AyakaContext()
