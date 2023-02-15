'''会话模型'''
import asyncio
from typing import Callable, Optional, TypeVar
from loguru import logger
from .helpers import simple_repr
from .context import ayaka_context

T = TypeVar("T")
'''任意类型'''


class AyakaSession:
    '''会话'''
    __session_type__ = ""

    def __init__(self, id: str) -> None:
        self.id: str = id
        self.state: str = ""
        '''状态'''

        self.cache: dict = {}
        '''缓存'''

        self._future: Optional[asyncio.Future] = None
        '''超时控制'''

        self._wait_next_msg_fut: Optional[asyncio.Future] = None

        self.last_cat_name: str = ""
        '''上一猫猫'''
        self.last_cat_time: int = 0
        '''上一猫猫访问时间'''

    @property
    def mark(self):
        return f"{self.__session_type__}.{self.id}"

    def has_last_wait_next_msg(self):
        if not self._wait_next_msg_fut:
            return False
        if self._wait_next_msg_fut.done():
            return False
        return True

    async def wait_next_msg(self):
        if self.has_last_wait_next_msg():
            self._wait_next_msg_fut.cancel()
            return

        self._wait_next_msg_fut = asyncio.Future()
        msg = await self._wait_next_msg_fut
        return msg

    def set_next_msg(self, msg: str):
        if not self.has_last_wait_next_msg():
            return

        self._wait_next_msg_fut.set_result(msg)

    def pop_data(self, factory: Callable[[], T]) -> T:
        '''弹出缓存数据

        参数:

            factory: 无参数的同步函数（类也可以）
        '''
        key = factory.__name__
        if key not in self.cache:
            return factory()
        return self.cache.pop(key)

    def get_data(self, factory: Callable[[], T]) -> T:
        '''获取缓存数据

        参数:

            factory: 无参数的同步函数（类也可以）
        '''
        key = factory.__name__
        if key not in self.cache:
            data = factory()
            self.cache[key] = data
        return self.cache[key]

    def __repr__(self) -> str:
        return simple_repr(self, exclude={"_future"})


class AyakaPrivate(AyakaSession):
    '''私聊会话'''
    __session_type__ = "private"

    @property
    def name(self):
        return ayaka_context.event.sender_name


class AyakaGroupMember(AyakaSession):
    '''群聊会话·群成员子会话'''
    __session_type__ = "group.member"

    @property
    def name(self):
        return ayaka_context.event.sender_name


class AyakaGroup(AyakaSession):
    '''群聊会话'''
    __session_type__ = "group"

    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.members: list[AyakaGroupMember] = []
        '''群成员'''

    @property
    def member(self):
        '''当前群成员'''
        sid = ayaka_context.event.sender_id
        for gm in self.members:
            if gm.id == sid:
                return gm
        gm = AyakaGroupMember(id=sid)
        self.members.append(gm)
        return gm


SessionClasses: list[type[AyakaSession]] = [AyakaPrivate, AyakaGroup]
'''session类列表'''


def get_session_cls(type: str) -> type[AyakaSession]:
    '''获取一个session类，尽力保证交付'''
    for cls in SessionClasses:
        if cls.__session_type__ == type:
            return cls

    logger.warning(f"未定义的会话类型 {type}，已尽力保证交付")

    class CustomSession(AyakaSession):
        __session_type__ = type

    SessionClasses.append(CustomSession)
    return CustomSession
