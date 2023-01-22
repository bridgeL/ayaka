'''
    在各地散装方法组成一个万能类

    比起继承来说，使用更灵活，没有拘束

    缺点是，你完全不记得自己都在哪里加的这些方法
'''
from typing import Awaitable, Callable
from .logger import logger
from .model import AyakaEvent, GroupMember
from .exception import NotRegistrationError, DuplicateRegistrationError
from .config import root_config


class AyakaBridge:
    def __init__(self) -> None:
        self.func_dict: dict[str, Callable] = {}

    def regist(self, func: Callable, name: str = ""):
        '''注册一个方法到bridge中，以供其他人调用，默认调用名称为该方法的名字'''
        name = name or func.__name__
        if name in self.func_dict:
            raise DuplicateRegistrationError(name)
        self.func_dict[name] = func

    def __getattr__(self, _name: str) -> None:
        '''获得先前注册的方法，通过self._func调用func方法'''
        name = _name.lstrip("_")
        if name not in self.func_dict:
            raise NotRegistrationError(name)
        return self.func_dict[name]

    # ---- ayaka cat 调用服务 ----
    async def send_group(self, id: str, msg: str) -> bool:
        return await self._send_group(id, msg)

    async def send_private(self, id: str, msg: str) -> bool:
        return await self._send_private(id, msg)

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
        return await self._send_group_many(id, msgs)
    
    async def send(self, type: str, id: str, msg: str) -> bool:
        '''待废弃'''
        return await self._send(type, id, msg)

    async def send_many(self, id: str, msgs: list[str]) -> bool:
        '''待废弃'''
        return await self._send_many(id, msgs)

    def get_prefixes(self) -> list[str]:
        return self._get_prefixes()

    def get_separates(self) -> list[str]:
        return self._get_separates()

    async def get_member_info(self, gid: str, uid: str) -> GroupMember | None:
        return await self._get_member_info(gid, uid)

    async def get_member_list(self, gid: str) -> list[GroupMember] | None:
        return await self._get_member_list(gid)

    def on_startup(self, func: Callable[..., Awaitable]):
        return self._on_startup(func)

    # ---- ayaka cat 提供服务 ----
    async def handle_event(self, event: "AyakaEvent") -> None:
        if root_config.error_report:
            try:
                await self._handle_event(event)
            except Exception as e:
                logger.exception("ayaka 处理事务时发生错误")
        else:
            await self._handle_event(event)


bridge = AyakaBridge()
