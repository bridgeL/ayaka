'''适配器基类'''
from contextvars import ContextVar
from loguru import logger
from typing import Awaitable, Callable
from .model import GroupMemberInfo, AyakaEvent
from ..logger import ayaka_clog

adapter_name_ctx: ContextVar[str] = ContextVar("adapter_name_ctx")


class AyakaAdapter:
    '''ayaka适配器，用于实现跨机器人框架和协议的兼容'''

    name: str = ""
    '''适配器名称'''
    prefixes: list[str] = []
    '''命令前缀'''
    separate: str = " "
    '''参数分隔符'''

    def first_init(self) -> None:
        '''在第一次初始化时执行'''
        raise NotImplementedError

    def on_startup(self, async_func: Callable[..., Awaitable]):
        '''asgi服务启动后钩子，注册回调必须是异步函数'''
        raise NotImplementedError

    async def send_group(self, id: str, msg: str) -> bool:
        '''发送消息到指定群聊'''
        raise NotImplementedError

    async def send_private(self, id: str, msg: str) -> bool:
        '''发送消息到指定私聊'''
        raise NotImplementedError

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
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
        # ---- 解除循环引用，待优化 ----
        from ..core import manager
        adapter_name_ctx.set(self.name)
        try:
            await manager.handle_event(ayaka_event)
        except:
            logger.exception(f"ayaka 处理事件（{ayaka_event}）时发生错误")


adapter_dict: dict[str, AyakaAdapter] = {}


def regist(adapter_cls: type[AyakaAdapter]):
    '''注册适配器'''
    name = adapter_cls.name
    if name in adapter_dict:
        return adapter_dict[name]

    adapter = adapter_cls()
    adapter.first_init()
    adapter_dict[name] = adapter
    ayaka_clog(f"ayaka适配器注册成功 <y>{name}</y>")
    return adapter


def get_first_adapter():
    adapters = list(adapter_dict.values())
    if adapters:
        return adapters[0]


def get_adapter(name: str = ""):
    '''获取ayaka适配器

    参数：

        name：适配器名称，若为空，则默认为当前上下文中的适配器，若当前上下文为空，则返回第一个适配器
    '''
    if not name:
        try:
            name = adapter_name_ctx.get()
        except LookupError:
            return get_first_adapter()

    return adapter_dict.get(name)
