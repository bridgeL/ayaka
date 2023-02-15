'''上下文'''
import asyncio
from typing import TYPE_CHECKING
from sqlmodel import Session
from .helpers import simple_repr, ContextGroup, Field
from .adapters import AyakaEvent

if TYPE_CHECKING:
    from .trigger import AyakaTrigger


def get_db_session():
    ayaka_context.db_session_flag = True
    ayaka_context.wait_tasks = []
    return ayaka_context.trigger.cat.db.get_session()


class AyakaContext(ContextGroup):
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
    '''是否使用了db_session'''

    def __repr__(self) -> str:
        return simple_repr(self)


ayaka_context = AyakaContext()
