'''上下文'''
from typing import TYPE_CHECKING, Optional
from contextvars import ContextVar
from ..helpers import simple_repr
from ..adapters import AyakaEvent

if TYPE_CHECKING:
    from .trigger import AyakaTrigger


class AyakaContext:
    '''上下文，保存一些数据便于访问'''

    def __init__(self, event: AyakaEvent) -> None:
        self.event: AyakaEvent = event
        self.trigger: Optional["AyakaTrigger"] = None
        self.cmd: Optional[str] = None
        self.arg: Optional[str] = None
        self.args: Optional[list[str]] = None
        self.nums: Optional[list[int]] = None

    def __repr__(self) -> str:
        return simple_repr(self)


_ayaka_context: ContextVar[AyakaContext] = ContextVar("_ayaka_context")


def set_context(event: AyakaEvent):
    context = AyakaContext(event)
    _ayaka_context.set(context)
    return context


def get_context():
    '''获取当前上下文'''
    return _ayaka_context.get()
