'''适配器基类'''
from loguru import logger
from contextvars import ContextVar
from typing import Awaitable, Callable
from .model import GroupMemberInfo, AyakaEvent
from .detect import is_hoshino, is_nb1, is_nb2ob11, is_no_env
from ..helpers import singleton
from ..logger import init_error_log
from ..config import get_root_config

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
    logger.opt(colors=True).debug(f"ayaka适配器注册成功 <y>{name}</y>")
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
    # 异味代码...但是不想改
    init_all()

    if not name:
        try:
            name = adapter_name_ctx.get()
        except LookupError:
            return get_first_adapter()

    return adapter_dict.get(name)


def auto_load_adapter():
    '''自动加载适配器'''

    # hoshino
    if is_hoshino():
        from .nb1.hoshino import HoshinoAdapter
        regist(HoshinoAdapter)

    # nonebot1
    if is_nb1():
        from .nb1.nb1 import Nonebot1Adapter
        regist(Nonebot1Adapter)

    # nonebot2 onebot11
    if is_nb2ob11():
        from .nb2.ob11 import Nonebot2Onebot11Adapter
        regist(Nonebot2Onebot11Adapter)

        if get_root_config().auto_ob11_qqguild_patch:
            from .nb2.qqguild_patch import Nonebot2Onebot11QQguildPatchAdapter
            regist(Nonebot2Onebot11QQguildPatchAdapter)

    if is_no_env():
        from .console import ConsoleAdapter
        regist(ConsoleAdapter)


# 异味代码...但是不想改
@singleton
def init_all():
    '''初始化ayaka，仅执行一次'''
    # 加载错误日志记录
    init_error_log()
    
    # 初始化根配置
    get_root_config()

    # 加载适配器
    auto_load_adapter()
    
    # 初始化 cat_block
    from ..core.cat_block import get_db

    # 加载猫猫管理器
    from .. import master
