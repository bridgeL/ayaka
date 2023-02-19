'''适配器基类'''
import sys
from loguru import logger
from contextvars import ContextVar
from pydantic import BaseModel
from typing import Awaitable, Callable, Optional
from ayaka_utils import is_async_callable, simple_async_wrap
from ..config import get_root_config


class GroupMemberInfo(BaseModel):
    id: str
    name: str
    role: Optional[str]
    '''群主、管理员、普通用户'''


class AyakaEvent(BaseModel):
    '''ayaka消息事件'''

    session_type: str
    '''消息会话类型'''
    session_id: str
    '''消息会话id'''
    sender_id: str
    '''消息发送者id'''
    sender_name: str
    '''消息发送者名称'''
    message: str
    '''当前消息'''
    reply: Optional[str]
    '''回复消息，如果gocq获取不到则为空字符串'''
    at: Optional[str]
    '''消息中的第一个at对象的uid'''
    raw_message: str
    '''从gocq收到的原始消息'''

    private_forward_id: Optional[str]
    '''私聊转发'''


def is_hoshino():
    if "hoshino" in sys.modules:
        logger.opt(colors=True).debug("识别到 <y>hoshino</y>")
        return True


def is_nb1():
    # 防止hoshino重复注册
    if "hoshino" not in sys.modules and "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            logger.opt(colors=True).debug("识别到 <y>nonebot1</y>")
            return True


def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        logger.opt(colors=True).debug("识别到 <y>nonebot2 onebot11</y>")
        return True


current_adapter: ContextVar["AyakaAdapter"] = ContextVar("current_adapter")


class AyakaAdapter:
    '''ayaka适配器，用于实现跨机器人框架和协议的兼容'''
    asgi = None

    name: str = ""
    '''适配器名称'''

    @property
    def prefixes(self):
        '''命令前缀'''
        return get_root_config().prefixes

    @property
    def separate(self):
        '''参数分隔符'''
        return get_root_config().separate

    def on_startup(self, func: Callable):
        '''asgi服务启动后钩子'''
        if not is_async_callable(func):
            func = simple_async_wrap(func)
        self._on_startup(func)

    def on_shutdown(self, func: Callable):
        '''asgi服务关闭后钩子'''
        if not is_async_callable(func):
            func = simple_async_wrap(func)
        self._on_shutdown(func)

    def _on_startup(self, async_func: Callable[..., Awaitable]):
        '''asgi服务启动后钩子，注册回调必须是异步函数'''
        raise NotImplementedError

    def _on_shutdown(self, async_func: Callable[..., Awaitable]):
        '''asgi服务关闭后钩子，注册回调必须是异步函数'''
        raise NotImplementedError

    async def send_group(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定群聊'''
        raise NotImplementedError

    async def send_private(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定私聊'''
        raise NotImplementedError

    async def send_group_many(self, id: str, msgs: list[str], bot_id: str | None = None) -> bool:
        '''发送消息组到指定群聊'''
        raise NotImplementedError

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
        raise NotImplementedError

    async def get_group_members(self, gid: str) -> list[GroupMemberInfo]:
        '''获取群内所有用户的信息'''
        raise NotImplementedError

    async def handle(self, *args, **kwargs):
        '''将输入的参数加工为ayaka_event，请在最后调用self.handle_event进行处理'''
        raise NotImplementedError

    async def handle_event(self, ayaka_event: AyakaEvent):
        '''处理ayaka事件，并在发生错误时记录'''
        current_adapter.set(self)
        try:
            # ---- 解除循环引用，待优化 ----
            from ..cat import manager
            await manager.handle_event(ayaka_event)
        except:
            logger.exception(f"ayaka 处理事件（{ayaka_event}）时发生错误")


adapter_dict: dict[str, AyakaAdapter] = {}
first_adapter: AyakaAdapter = None


def get_first_adapter():
    return first_adapter


def regist(adapter_cls: type[AyakaAdapter]):
    '''注册适配器'''

    name = adapter_cls.name
    if name in adapter_dict:
        return adapter_dict[name]

    adapter = adapter_cls()

    if not adapter_dict:
        global first_adapter
        first_adapter = adapter

    adapter_dict[name] = adapter
    logger.opt(colors=True).debug(f"ayaka适配器注册成功 <y>{name}</y>")
    return adapter


def get_adapter(name: str = ""):
    '''获取ayaka适配器

    参数：

        name：返回对应名称的适配器

        若为空，则返回当前上下文中的适配器

        若当前上下文为空，则返回第一个注册的适配器
    '''
    if not name:
        return current_adapter.get(first_adapter)
    return adapter_dict.get(name)


def auto_load_adapter():
    '''自动加载适配器'''

    # hoshino
    if is_hoshino():
        from .nb1.hoshino import HoshinoAdapter

    # nonebot1
    elif is_nb1():
        from .nb1.nb1 import Nonebot1Adapter

    # nonebot2 onebot11
    elif is_nb2ob11():
        from .nb2.ob11 import Nonebot2Onebot11Adapter

    else:
        from .console import ConsoleAdapter


auto_load_adapter()


@first_adapter.on_startup
async def _():
    '''初始化所有数据库'''
    from ..database import db_dict
    for db in db_dict.values():
        db.init()
