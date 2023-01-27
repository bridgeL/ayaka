'''
    在各地散装方法组成一个万能类

    比起继承来说，使用更灵活，没有拘束

    缺点是，你完全不记得自己都在哪里加的这些方法
'''
from pydantic import BaseModel
from typing import Awaitable, Callable, Optional
from .event import AyakaEvent
from .exception import NotRegistrationError, DuplicateRegistrationError


class GroupMemberInfo(BaseModel):
    id: str
    name: str
    role: Optional[str]
    '''群主、管理员、普通用户'''


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

    def get_prefixes(self) -> list[str]:
        return self._get_prefixes()

    async def get_member_info(self, gid: str, uid: str) -> GroupMemberInfo | None:
        return await self._get_member_info(gid, uid)

    async def get_member_list(self, gid: str) -> list[GroupMemberInfo] | None:
        return await self._get_member_list(gid)

    def on_startup(self, func: Callable[..., Awaitable]):
        return self._on_startup(func)

    # ---- ayaka cat 提供服务 ----
    async def handle_event(self, event: "AyakaEvent") -> None:
        await self._handle_event(event)


bridge = AyakaBridge()
