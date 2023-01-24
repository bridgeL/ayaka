'''上下文'''
from typing import TYPE_CHECKING, Optional
from contextvars import ContextVar
from .event import AyakaEvent
from .helpers import simple_repr

if TYPE_CHECKING:
    from .trigger import AyakaTrigger


class AyakaContext:
    def __init__(self) -> None:
        self.event: Optional[AyakaEvent] = None
        self.trigger: Optional["AyakaTrigger"] = None
        self.cmd: Optional[str] = None
        self.arg: Optional[str] = None
        self.args: Optional[list[str]] = None
        self.nums: Optional[list[int]] = None

    def __repr__(self) -> str:
        return simple_repr(self)


_ayaka_context: ContextVar[AyakaContext] = ContextVar("_ayaka_context", default=None)


def get_context():
    '''获取当前上下文'''
    c = _ayaka_context.get()
    if c:
        return c
    c = AyakaContext()
    _ayaka_context.set(c)
    return c
