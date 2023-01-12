'''
    ayaka核心

    猫猫类
'''
import re
import sys
import inspect
import asyncio
from contextvars import ContextVar
from typing import Awaitable, Callable, TypeVar
from pydantic import BaseModel
from loguru import logger
from .helpers import ensure_list, simple_repr
from .config import root_config
from .model import AyakaSession, AyakaEvent
from .exception import BlockException, NotBlockException, DuplicateCatNameError, CannotFindModuleError
from .bridge import bridge

_event: ContextVar["AyakaEvent"] = ContextVar("_event")
_params: ContextVar["AyakaParams"] = ContextVar("_params")

T = TypeVar("T")
'''任意类型'''


class AyakaCurrent:
    def __init__(self) -> None:
        self._cat_dict: dict[str, AyakaCat] = {}

    @property
    def event(self):
        '''当前会话消息事件'''
        return _event.get()

    @property
    def msg(self):
        '''当前会话消息'''
        return self.event.msg

    @property
    def session(self):
        '''当前会话'''
        return self.event.session

    @property
    def session_type(self):
        '''当前会话type'''
        return self.session.type

    @property
    def session_id(self):
        '''当前会话id，群聊为group_id，私聊为user_id'''
        return self.session.id

    @property
    def session_mark(self):
        '''当前会话标识'''
        return self.session.mark

    @property
    def sender_id(self):
        '''当前消息发送者的id'''
        return self.event.sender_id

    @property
    def sender_name(self):
        '''当前消息发送者的name'''
        return self.event.sender_name

    @property
    def cat(self):
        '''当前cat'''
        return self._cat_dict.get(self.session_mark)

    @cat.setter
    def cat(self, cat: "AyakaCat"):
        self._cat_dict[self.session_mark] = cat

    @property
    def desktop_mode(self):
        '''当前桌面模式标识'''
        return not self.cat

    @property
    def params(self):
        '''当前参数'''
        return _params.get()

    @property
    def trigger(self):
        '''当前触发器'''
        return self.params.trigger

    @property
    def cmd(self):
        '''当前触发命令'''
        return self.params.cmd

    @property
    def arg(self):
        '''当前消息移除命令后的内容'''
        return self.params.arg

    @property
    def args(self):
        '''当前消息移除命令后的内容进一步分割'''
        return self.params.args

    @property
    def nums(self):
        '''当前消息中的的整数数字'''
        return self.params.nums


class AyakaParams:
    def __init__(self, trigger: "AyakaTrigger") -> None:
        self.trigger = trigger
        self.cmd = trigger.cmd

        prefix = bridge.get_prefix()
        separate = bridge.get_separate()

        self.arg = current.msg[len(prefix+self.cmd):].strip(separate)
        self.args = [arg for arg in self.arg.split(separate) if arg]

        pt = re.compile(r"^-?\d+$")
        self.nums = [int(arg) for arg in self.args if pt.search(arg)]

    def __repr__(self) -> str:
        return simple_repr(self)


class AyakaManager:
    def __init__(self) -> None:
        self.cats: list[AyakaCat] = []
        self.always_triggers: list[AyakaTrigger] = []
        self.desktop_triggers: list[AyakaTrigger] = []
        self.state_trigger_dict: dict[str, dict[str, list[AyakaTrigger]]] = {}
        self.listen_dict: dict[AyakaSession, list[AyakaSession]] = {}
        '''target:list[listener]'''

    @property
    def state_triggers(self):
        data = self.state_trigger_dict.get(current.cat.name)
        if not data:
            return []
        return data.get(current.cat.state, [])

    @property
    def star_state_triggers(self):
        data = self.state_trigger_dict.get(current.cat.name)
        if not data:
            return []
        return data.get("*", [])

    def add_always_trigger(self, trigger: "AyakaTrigger"):
        self.always_triggers.append(trigger)
        self.always_triggers.sort(key=lambda t: len(t.cmd), reverse=True)

    def add_desktop_trigger(self, trigger: "AyakaTrigger"):
        self.desktop_triggers.append(trigger)
        self.desktop_triggers.sort(key=lambda t: len(t.cmd), reverse=True)

    def add_state_trigger_dict(self, trigger: "AyakaTrigger"):
        self.state_trigger_dict.setdefault(trigger.cat.name, {})
        data = self.state_trigger_dict[trigger.cat.name]

        data.setdefault(trigger.state, [])
        data = data[trigger.state]

        data.append(trigger)
        data.sort(key=lambda t: len(t.cmd), reverse=True)

    async def _handle_event(self, event: AyakaEvent):
        '''处理消息'''
        # 设置上下文
        _event.set(event)

        # 收集并处理所有cats中的always触发
        for trigger in self.always_triggers:
            if await trigger.run():
                return

        # if 桌面模式
        if current.desktop_mode:
            # 收集并处理所有cats中的desktop触发
            for trigger in self.desktop_triggers:
                if await trigger.run():
                    return

        # else
        else:
            # 收集并处理当前cat中的状态触发
            # 优先处理state = "*"
            for trigger in self.star_state_triggers:
                if await trigger.run():
                    return

            # 处理当前状态
            for trigger in self.state_triggers:
                if await trigger.run():
                    return

    async def handle_event(self, event: AyakaEvent):
        '''处理消息和转发情况'''
        await self._handle_event(event)
        target = event.session
        v = self.listen_dict.get(target, [])

        ts = []
        for listener in v:
            data = event.dict()
            data.update(session=listener, origin=event)
            _event = AyakaEvent(**data)
            ts.append(asyncio.create_task(self._handle_event(_event)))
        await asyncio.gather(*ts)

    def add_cat(self, cat: "AyakaCat"):
        for c in self.cats:
            if c.name == cat.name:
                raise DuplicateCatNameError(cat.name)
        self.cats.append(cat)

    def get_cat(self, name: str):
        for c in self.cats:
            if c.name == name:
                return c

    def add_listener(self, listener: AyakaSession, target: AyakaSession):
        self.listen_dict.setdefault(target, [])
        self.listen_dict[target].append(listener)

    def remove_listener(self, listener: AyakaSession, target: AyakaSession | None = None):
        if not target:
            ks = []
            for k, v in self.listen_dict.items():
                if listener in v:
                    v.remove(listener)
                if not v:
                    ks.append(k)
            for k in ks:
                self.listen_dict.pop(k)
        else:
            k = target
            v = self.listen_dict.get(k, [])
            if listener in v:
                v.remove(listener)
            if not v:
                self.listen_dict.pop(k)


class AyakaTrigger:
    def __init__(self, func: Callable[[], Awaitable], cat: "AyakaCat", session_types: list[str] = ["group"], cmd: str = "", state: str = "", always: bool = False, block: bool = False) -> None:
        self.session_types = session_types
        self.cmd = cmd
        '''顺便可以区分命令触发和文本触发'''
        self.state = state
        '''顺便可以区分desktop和state'''
        self.always = always
        self.block = block
        self.func = func
        self.cat = cat

        if self.always:
            manager.add_always_trigger(self)
        elif self.desktop:
            manager.add_desktop_trigger(self)
        else:
            manager.add_state_trigger_dict(self)

    @property
    def desktop(self):
        return not self.state

    @property
    def func_name(self):
        return self.func.__name__

    @property
    def module_name(self):
        return self.func.__module__

    async def run(self):
        # 判断是否被屏蔽
        if not self.cat.valid:
            return False

        # 范围是否符合
        if not current.session_type in self.session_types:
            return False

        prefix = bridge.get_prefix()

        # if 命令触发，命令是否符合
        if self.cmd and not current.msg.startswith(prefix + self.cmd):
            return False

        # 一些预处理，并保存到上下文中
        params = AyakaParams(self)
        _params.set(params)

        # 打印日志
        items = [f"<y>猫猫</y> {self.cat.name}"]
        if self.cmd:
            items.append(f"<y>命令</y> {self.cmd}")
        else:
            items.append("<g>文字</g>")
        if self.state:
            items.append(f"<c>状态</c> {self.state}")
        items.append(f"<y>回调</y> {self.func_name}")
        logger.opt(colors=True).debug(" | ".join(items))
        
        # 运行函数
        try:
            await self.func()
        except BlockException:
            return True
        except NotBlockException:
            return False

        # 返回是否阻断
        return self.block

    def __repr__(self) -> str:
        return simple_repr(self, cat=self.cat.name, func=self.func_name, module=self.module_name, exclude={"session_types"})


class AyakaCat:
    def __init__(self, name: str, session_types: str | list[str] = "group") -> None:
        self.name = name
        manager.add_cat(self)

        self.module_path = inspect.stack()[1].filename
        keys = list(sys.modules.keys())
        n = len(keys)
        for i in range(n):
            k = keys[n-i-1]
            v = sys.modules[k]
            if v.__file__ == self.module_path:
                self.module_name = k
                break
        else:
            raise CannotFindModuleError(self.module_path)

        self.current = current
        self.session_types = ensure_list(session_types)
        self._state_dict: dict[str, str] = {}
        self._cache_dict: dict[str, dict] = {}
        self.triggers: list[AyakaTrigger] = []
        self._intro = ""
        self._helps: dict[str, list] = {}
        self._invalid_list = root_config.block_cat_dict.get(name, [])

    # ---- 便捷属性 ----
    @property
    def state(self):
        '''猫猫状态'''
        self._state_dict.setdefault(current.session_mark, "idle")
        return self._state_dict[current.session_mark]

    @state.setter
    def state(self, value: str):
        self.set_state(value)

    @property
    def cache(self):
        '''猫猫缓存'''
        self._cache_dict.setdefault(current.session_mark, {})
        return self._cache_dict[current.session_mark]

    @property
    def params(self):
        return _params.get()

    @property
    def help(self):
        '''猫猫帮助'''
        items = [f"[{self.name}]"]
        if self._intro:
            items.append(self._intro)
        items.extend(self._helps.get("", []))

        for state, infos in self._helps.items():
            if not state:
                continue
            items.append(f"[{state}]")
            items.extend(infos)

        return "\n".join(items)

    @help.setter
    def help(self, value: str):
        self._intro = value.strip()

    @property
    def valid(self):
        '''当前猫猫是否可用'''
        return self.current.session not in self._invalid_list

    @valid.setter
    def valid(self, value: bool):
        '''设置当前猫猫是否可用'''
        change_flag = False
        if value and not self.valid:
            self._invalid_list.remove(self.current.session)
            change_flag = True

        elif not value and self.valid:
            self._invalid_list.append(self.current.session)
            change_flag = True

        if change_flag:
            if self._invalid_list:
                root_config.block_cat_dict[self.name] = self._invalid_list
            else:
                root_config.block_cat_dict.pop(self.name, None)
            root_config.save()

    # ---- on_xxx ----
    def on_cmd(self, cmds: str | list[str] = "", states: str | list[str] = "", session_types: str | list[str] | None = None, always: bool = False, block: bool = True, auto_help: bool = True):
        cmds = ensure_list(cmds)
        states = ensure_list(states)
        if session_types:
            session_types = ensure_list(session_types)
        else:
            session_types = self.session_types

        def decorator(func: Callable[[], Awaitable]):
            if auto_help:
                self._add_help(cmds, states, func)
            if always:
                for cmd in cmds:
                    self.triggers.append(AyakaTrigger(
                        func=func, cat=self, session_types=session_types,
                        cmd=cmd, always=True, block=block
                    ))
            else:
                for cmd in cmds:
                    for state in states:
                        self.triggers.append(AyakaTrigger(
                            func=func, cat=self, session_types=session_types,
                            cmd=cmd, state=state, block=block
                        ))
            return func
        return decorator

    def on_text(self, states: str | list[str] = "", session_types: str | list[str] | None = None, always: bool = False, block: bool = False, auto_help: bool = True):
        return self.on_cmd(states=states, session_types=session_types, always=always, block=block, auto_help=auto_help)

    # ---- 添加帮助 ----
    def _add_help(self, cmds: list[str], states: list[str], func: Callable[[], Awaitable]):
        '''添加帮助

        参数:

            cmds: 命令

            states: 状态

            func: 回调
        '''
        info = "- "
        if cmds and cmds[0]:
            info += "/".join(cmds) + " "
        else:
            info += "<任意文字> "
        if func.__doc__:
            info += func.__doc__
        for state in states:
            if state not in self._helps:
                self._helps[state] = [info]
            else:
                self._helps[state].append(info)

    # ---- 设置状态 ----
    def set_state(self, state: str):
        '''修改猫猫状态

        参数: 

            state: 新状态

        异常:

            state不可为空字符串或*
        '''
        if state in ["", "*"]:
            raise Exception("state不可为空字符串或*")
        self._state_dict[current.session_mark] = state

    async def start(self, state: str = "idle"):
        '''留给古板的老学究用'''
        await self.wakeup(state)

    async def close(self):
        '''留给古板的老学究用'''
        await self.rest()

    async def wakeup(self, state: str = "idle"):
        '''唤醒猫猫，唤醒后猫猫状态默认为idle

        参数: 

            state: 新状态

        异常:

            state不可为空字符串或*
        '''
        if self.current.desktop_mode:
            self.current.cat = self
            self.state = state
            await self.send(f"已唤醒猫猫[{self.name}]")

    async def rest(self):
        '''猫猫休息'''
        if self.current.cat == self:
            self.current.cat = None
            await self.send(f"[{self.name}]猫猫休息了")

    # ---- 发送 ----
    async def base_send(self, session: AyakaSession, msg: str):
        await bridge.send(session.type, session.id, msg)

    async def base_send_many(self, session: AyakaSession,  msgs: list[str]):
        await bridge.send_many(session.id, msgs)

    # ---- 快捷发送 ----
    async def send(self, msg: str):
        await self.base_send(current.session, msg)

    async def send_many(self, msgs: list[str]):
        await self.base_send_many(current.session, msgs)

    async def send_help(self):
        '''发送自身帮助'''
        await self.send(self.help)

    # ---- cache ----
    def remove_data(self, key_or_obj: str | BaseModel):
        '''从当前群组的缓存移除指定的键-值对

        参数:

            key: 键名或BaseModel对象，如果是BaseModel对象，则自动取其类的名字作为键名

        异常:

            参数类型错误，必须是字符串或BaseModel对象
        '''
        if isinstance(key_or_obj, str):
            key = key_or_obj
        elif isinstance(key_or_obj, BaseModel):
            key = key_or_obj.__class__.__name__
        else:
            raise Exception("参数类型错误，必须是字符串或BaseModel对象")
        self.cache.pop(key, None)

    def get_data(self, factory: Callable[[], T], key: str = None) -> T:
        '''从当前缓存中获取数据

        参数:

            factory: 任何无参数的制造对象的函数（类也可以）

            key: 键名，为空时使用factory.__name__作为键名

        返回:

            factory生产对象
        '''
        if key is None:
            key = factory.__name__
        if key not in self.cache:
            data = factory()
            self.cache[key] = data
            return data
        return self.cache[key]

    # ---- 快捷命令 ----
    def set_wakeup_cmds(self, cmds: str | list[str]):
        '''设置唤醒命令'''
        @self.on_cmd(cmds=cmds)
        async def wakeup():
            '''唤醒猫猫'''
            await self.wakeup()
            await self.send_help()
        wakeup.__module__ = self.module_name

    def set_rest_cmds(self, cmds: str | list[str]):
        '''设置休息命令'''
        @self.on_cmd(cmds=cmds, states="*")
        async def rest():
            '''猫猫休息'''
            await self.rest()
        rest.__module__ = self.module_name

    # ---- 消息监听 ----
    def add_listener(self, target: AyakaSession):
        listener = current.session
        manager.add_listener(listener, target)

    def remove_listener(self, target: AyakaSession | None = None):
        listener = current.session
        manager.remove_listener(listener, target)

    # ---- 其他 ----
    async def get_user(self, uid: str):
        return await bridge.get_member_info(self.current.session_id, uid)

    async def get_users(self):
        return await bridge.get_member_list(self.current.session_id)


current = AyakaCurrent()
manager = AyakaManager()

# 注册内部服务
bridge.regist(manager.handle_event)
