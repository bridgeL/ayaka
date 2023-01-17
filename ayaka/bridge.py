'''
    在各地散装方法组成一个万能类

    比起继承来说，使用更灵活，没有拘束

    缺点是，你完全不记得自己都在哪里加的这些方法
'''
from typing import Awaitable, Callable
from .model import AyakaEvent, User
from .exception import NotRegistrationError, DuplicateRegistrationError


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
    async def send(self, type: str, id: str, msg: str) -> None:
        await self._send(type, id, msg)

    async def send_many(self, id: str, msgs: list[str]) -> None:
        await self._send_many(id, msgs)

    def get_prefixes(self) -> list[str]:
        return self._get_prefixes()

    def get_separates(self) -> list[str]:
        return self._get_separates()

    async def get_member_info(self, gid: str, uid: str) -> User | None:
        return await self._get_member_info(gid, uid)

    async def get_member_list(self, gid: str) -> list[User] | None:
        return await self._get_member_list(gid)

    def on_startup(self, func: Callable[..., Awaitable]):
        return self._on_startup(func)

    # ---- ayaka cat 提供服务 ----
    async def handle_event(self, event: "AyakaEvent") -> None:
        await self._handle_event(event)


bridge = AyakaBridge()
