'''上下文'''
import asyncio
from typing import TYPE_CHECKING, Optional
from ayaka_utils import ContextGroup, Field

if TYPE_CHECKING:
    from sqlmodel import Session as DBSession
    from .trigger import AyakaTrigger
    from .cat import AyakaCat
    from .adapters import AyakaEvent, AyakaAdapter


def _get_db_session():
    ayaka_context.db_session_flag = True
    ayaka_context.wait_tasks = []
    return ayaka_context.cat.db.get_session()


class AyakaContext(ContextGroup):
    '''上下文，保存一些数据便于访问'''

    event: "AyakaEvent"
    '''消息事件'''

    cat: "AyakaCat"
    '''当前猫猫'''

    adapter: Optional["AyakaAdapter"] = None
    '''当前适配器'''

    trigger: "AyakaTrigger"
    '''当前触发器'''

    prefix: Optional[str] = None
    '''当前命令前缀'''

    cmd: str = ""
    '''当前命令'''

    arg: str = ""
    '''去掉命令的剩余文字'''

    args: list[str] = []
    '''剩余文字根据separate分割'''

    nums: list[int] = []
    '''数字'''

    wait_tasks: list[asyncio.Task] = []
    '''数据库会话关闭前，会等待该队列中的所有任务结束'''

    db_session: "DBSession" = Field(default_factory=_get_db_session)
    '''数据库会话，请在trigger存在的时候使用'''

    db_session_flag: bool = False
    '''是否使用了db_session'''


ayaka_context = AyakaContext()
