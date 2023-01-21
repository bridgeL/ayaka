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
from .logger import logger, clogger
from .helpers import ensure_list, simple_repr
from .config import root_config
from .model import AyakaChannel, AyakaEvent
from .exception import BlockException, NotBlockException, DuplicateCatNameError, CannotFindModuleError
from .bridge import bridge

_event: ContextVar["AyakaEvent"] = ContextVar("_event")
_params: ContextVar["AyakaParams"] = ContextVar("_params")

T = TypeVar("T")
'''任意类型'''


class AyakaParams:
    def __init__(self, trigger: "AyakaTrigger", prefix: str) -> None:
        self.trigger = trigger
        self.cmd = trigger.cmd

        separates = bridge.get_separates()
        if " " in separates:
            separate = " "
        else:
            separate = separates[0]

        self.arg = manager.event.message[len(prefix+self.cmd):].strip(separate)
        self.args = [arg for arg in self.arg.split(separate) if arg]

        pt = re.compile(r"^-?\d+$")
        self.nums = [int(arg) for arg in self.args if pt.search(arg)]

    def __repr__(self) -> str:
        return simple_repr(self)


class AyakaManager:
    '''分发ayaka event'''

    def __init__(self) -> None:
        self.cats: list[AyakaCat] = []
        self.always_triggers: list[AyakaTrigger] = []
        self.desktop_triggers: list[AyakaTrigger] = []
        self.state_trigger_dict: dict[str, dict[str, list[AyakaTrigger]]] = {}
        self.listen_dict: dict[AyakaChannel, list[AyakaChannel]] = {}
        '''key为被监听者，value为监听者数组'''
        self._cat_dict: dict[str, AyakaCat] = {}
        '''所有频道的猫猫'''

    @property
    def event(self):
        return _event.get()

    @property
    def current_cat(self):
        return self._cat_dict.get(self.event.channel.mark)

    @current_cat.setter
    def current_cat(self, value):
        self._cat_dict[self.event.channel.mark] = value

    @property
    def params(self):
        return _params.get()

    @params.setter
    def params(self, value):
        return _params.set(value)

    @property
    def state_triggers(self):
        data = self.state_trigger_dict.get(self.current_cat.name)
        if not data:
            return []
        return data.get(self.current_cat.state, [])

    @property
    def star_state_triggers(self):
        data = self.state_trigger_dict.get(self.current_cat.name)
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

    async def base_handle_event(self, event: AyakaEvent):
        '''处理事件'''
        # 设置上下文
        _event.set(event)

        prefixes = bridge.get_prefixes()

        # 收集并处理所有cats中的always触发
        for trigger in self.always_triggers:
            for prefix in prefixes:
                if await trigger.run(prefix):
                    return

        # if 桌面模式
        if not self.current_cat:
            # 收集并处理所有cats中的desktop触发
            for trigger in self.desktop_triggers:
                for prefix in prefixes:
                    if await trigger.run(prefix):
                        return

        # else
        else:
            # 收集并处理当前cat中的状态触发
            # 优先处理state = "*"
            for trigger in self.star_state_triggers:
                for prefix in prefixes:
                    if await trigger.run(prefix):
                        return

            # 处理当前状态
            for trigger in self.state_triggers:
                for prefix in prefixes:
                    if await trigger.run(prefix):
                        return

    async def handle_event(self, event: AyakaEvent):
        '''处理和转发事件'''
        await self.base_handle_event(event)
        target = event.channel
        ts = []
        for listener in self.listen_dict.get(target, []):
            data = event.dict()
            data.update(channel=listener, origin_channel=target)
            _event = AyakaEvent(**data)
            ts.append(asyncio.create_task(self.base_handle_event(_event)))
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

    def add_listener(self, listener: AyakaChannel, target: AyakaChannel):
        self.listen_dict.setdefault(target, [])
        self.listen_dict[target].append(listener)

    def remove_listener(self, listener: AyakaChannel, target: AyakaChannel | None = None):
        # 移除所有监听
        if not target:
            empty_targets = []

            # 遍历监听表
            for target, listeners in self.listen_dict.items():
                # 移除监听
                if listener in listeners:
                    listeners.remove(listener)

                # 统计所有无监听者的目标
                if not listeners:
                    empty_targets.append(target)

            # 移除这些无监听者的目标
            for target in empty_targets:
                self.listen_dict.pop(target)

        # 移除指定监听
        else:
            listeners = self.listen_dict.get(target, [])

            # 移除监听
            if listener in listeners:
                listeners.remove(listener)

            # 移除无监听者的目标
            if not listeners:
                self.listen_dict.pop(target)


class AyakaTrigger:
    def __init__(self, func: Callable[[], Awaitable], cat: "AyakaCat", cmd: str = "", state: str = "", always: bool = False, block: bool = False) -> None:
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
        elif not self.state:
            manager.add_desktop_trigger(self)
        else:
            manager.add_state_trigger_dict(self)

    @property
    def func_name(self):
        return self.func.__name__

    @property
    def module_name(self):
        return self.func.__module__

    async def run(self, prefix):
        # 判定范围
        if manager.event.channel.type not in self.cat.channel_types:
            return False

        # 判断是否被屏蔽
        if not self.cat.valid:
            return False

        # if 命令触发，命令是否符合
        if self.cmd and not manager.event.message.startswith(prefix + self.cmd):
            return False

        # 重设超时定时器
        self.cat._start_overtime_timer()

        # 一些预处理，并保存到上下文中
        manager.params = AyakaParams(self, prefix)

        # 打印日志
        items = [f"<y>猫猫</y> {self.cat.name}"]
        if self.cmd:
            items.append(f"<y>命令</y> {self.cmd}")
        else:
            items.append("<g>文字</g>")
        if self.state:
            items.append(f"<c>状态</c> {self.state}")
        items.append(f"<y>回调</y> {self.func_name}")
        clogger.debug(" | ".join(items))

        # 运行函数
        try:
            await self.func()
        except BlockException:
            logger.info("BlockException")
            return True
        except NotBlockException:
            logger.info("NotBlockException")
            return False

        # 返回是否阻断
        return self.block

    def __repr__(self) -> str:
        return simple_repr(
            self,
            cat=self.cat.name,
            func=self.func_name,
            module=self.module_name
        )


class AyakaCat:
    def __init__(
        self,
        name: str,
        overtime: int = 600,
        channel_types: str | list[str] = "group",
    ) -> None:
        '''创建猫猫

        参数：

            name：猫猫名字

            overtime：超时未收到指令则自动关闭，单位：秒

            channel_types：默认为群聊插件（不建议更改）
        '''
        self.name = name
        manager.add_cat(self)

        self.module_path = inspect.stack()[1].filename
        keys = list(sys.modules.keys())
        n = len(keys)
        for i in range(n):
            k = keys[n-i-1]
            v = sys.modules[k]
            if getattr(v, "__file__", "") == self.module_path:
                self.module_name = k
                break
        else:
            raise CannotFindModuleError(self.module_path)

        self.overtime = overtime
        self.channel_types = ensure_list(channel_types)
        self._state_dict: dict[str, str] = {}
        self._cache_dict: dict[str, dict] = {}
        self._fut_dict: dict[str, asyncio.Future] = {}
        self.triggers: list[AyakaTrigger] = []
        self._intro = ""
        self._helps: dict[str, list] = {}
        self._invalid_list = root_config.block_cat_dict.get(name, [])

    # ---- 超时控制 ----
    def _start_overtime_timer(self):
        if not self.overtime:
            return

        if manager.current_cat != self:
            return

        self._stop_overtime_timer()

        loop = asyncio.get_event_loop()
        self.fut = loop.create_future()
        loop.create_task(self._overtime_handle())

    async def _overtime_handle(self):
        try:
            await asyncio.wait_for(self.fut, self.overtime)
        except asyncio.exceptions.TimeoutError:
            await self.send("猫猫超时")
            await self.rest()

    def _stop_overtime_timer(self):
        if not self.fut:
            return
        if self.fut.done():
            return
        if self.fut.cancelled():
            return

        self.fut.set_result(True)

    # ---- 便捷属性 ----
    @property
    def fut(self):
        '''猫猫超时记录'''
        return self._fut_dict.get(self.channel.mark)

    @fut.setter
    def fut(self, value: asyncio.Future):
        self._fut_dict[self.channel.mark] = value

    @property
    def state(self):
        '''猫猫状态'''
        return self._state_dict[self.channel.mark]

    @state.setter
    def state(self, value: str):
        self.set_state(value)

    @property
    def cache(self):
        '''猫猫缓存'''
        self._cache_dict.setdefault(self.channel.mark, {})
        return self._cache_dict[self.channel.mark]

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
        return self.channel not in self._invalid_list

    @valid.setter
    def valid(self, value: bool):
        '''设置当前猫猫是否可用'''
        change_flag = False
        if value and not self.valid:
            self._invalid_list.remove(self.channel)
            change_flag = True

        elif not value and self.valid:
            self._invalid_list.append(self.channel)
            change_flag = True

        if change_flag:
            if self._invalid_list:
                root_config.block_cat_dict[self.name] = self._invalid_list
            else:
                root_config.block_cat_dict.pop(self.name, None)
            root_config.save()

    @property
    def event(self):
        '''当前事件'''
        return _event.get()

    @property
    def channel(self):
        '''当前频道'''
        return self.event.channel

    @property
    def user(self):
        '''当前用户'''
        return self.event.sender

    @property
    def message(self):
        '''当前消息'''
        return self.event.message

    @property
    def trigger(self):
        '''当前触发器'''
        return manager.params.trigger

    @property
    def cmd(self):
        '''当前触发命令'''
        return manager.params.cmd

    @property
    def arg(self):
        '''当前消息移除命令后的内容'''
        return manager.params.arg

    @property
    def args(self):
        '''当前消息移除命令后的内容进一步分割'''
        return manager.params.args

    @property
    def nums(self):
        '''当前消息中的的整数数字'''
        return manager.params.nums

    # ---- on_xxx ----
    def on_cmd(
        self,
        cmds: str | list[str] = "",
        states: str | list[str] = "",
        always: bool = False,
        block: bool = True,
        auto_help: bool = True
    ):
        '''注册命令回调

        参数：

            cmds：命令或命令数组

            states：状态或状态数组

            always：总是第一个触发，不受ayaka的状态约束控制

            block：触发后阻断事件继续传播

            auto_help：不要自动生成猫猫帮助
        '''
        cmds = ensure_list(cmds)
        states = ensure_list(states)

        def decorator(func: Callable[[], Awaitable]):
            if auto_help:
                self._add_help(cmds, states, func)
            if always:
                for cmd in cmds:
                    self.triggers.append(AyakaTrigger(
                        func=func,
                        cat=self,
                        cmd=cmd,
                        always=True,
                        block=block
                    ))
            else:
                for cmd in cmds:
                    for state in states:
                        self.triggers.append(AyakaTrigger(
                            func=func,
                            cat=self,
                            cmd=cmd,
                            state=state,
                            block=block
                        ))
            clogger.trace(
                f"<y>猫猫</y> {self.name} | <y>命令</y> {cmds} | <y>状态</y> {states} | <y>回调</y> {func.__name__}")
            return func
        return decorator

    def on_text(
        self,
        states: str | list[str] = "",
        always: bool = False,
        block: bool = False,
        auto_help: bool = True
    ):
        '''注册文字回调

        参数：

            states：状态或状态数组

            always：总是第一个触发，不受ayaka的状态约束控制

            block：触发后阻断事件继续传播

            auto_help：不要自动生成猫猫帮助
        '''
        return self.on_cmd(states=states, always=always, block=block, auto_help=auto_help)

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
    def set_state(self, value: str):
        '''设置指定频道的状态

        参数: 

            state: 新状态

        异常:

            state不可为空字符串或*
        '''
        if value in ["", "*"]:
            raise Exception("state不可为空字符串或*")
        self._state_dict[self.channel.mark] = value

        # 重设超时定时器
        self._start_overtime_timer()

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
        if not manager.current_cat:
            manager.current_cat = self
            self.state = state
            await self.send(f"已唤醒猫猫[{self.name}]")
            self._start_overtime_timer()

    async def rest(self):
        '''猫猫休息'''
        if manager.current_cat == self:
            manager.current_cat = None
            await self.send(f"[{self.name}]猫猫休息了")
            self._stop_overtime_timer()

    # ---- 发送 ----
    async def base_send(self, channel: AyakaChannel, msg: str):
        '''发送消息至指定频道'''
        # 重设超时定时器
        self._start_overtime_timer()
        # 发送消息
        return await bridge.send(channel.type, channel.id, msg)

    async def base_send_many(self, channel: AyakaChannel,  msgs: list[str]):
        '''发送消息组至指定频道'''
        # 重设超时定时器
        self._start_overtime_timer()
        # 发送消息
        if channel.type == "group":
            return await bridge.send_many(channel.id, msgs)
        # 其他类型的频道不支持合并转发
        return await self.base_send(channel, "\n".join(msgs))

    # ---- 快捷发送 ----
    async def send(self, msg: str):
        '''发送消息至当前频道'''
        return await self.base_send(self.channel, msg)

    async def send_many(self, msgs: list[str]):
        '''发送消息组至当前频道'''
        return await self.base_send_many(self.channel, msgs)

    async def send_help(self):
        '''发送自身帮助'''
        await self.send(self.help)

    # ---- cache ----
    def pop_data(self, factory: Callable[[], T]) -> T:
        '''从当前群组的缓存弹出指定的键值

        参数:

            factory: 任何无参数的制造对象的函数（类也可以）
        '''
        key = factory.__name__
        if key not in self.cache:
            return factory()
        return self.cache.pop(key)

    def get_data(self, factory: Callable[[], T]) -> T:
        '''从当前缓存中获取数据

        参数:

            factory: 任何无参数的制造对象的函数（类也可以）

        返回:

            factory生产对象
        '''
        key = factory.__name__
        if key not in self.cache:
            data = factory()
            self.cache[key] = data
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
    def add_listener(self, target: AyakaChannel):
        '''添加当前频道A对指定频道B的监听，当B收到消息后，会转发一份副本给A处理'''
        manager.add_listener(self.channel, target)

    def remove_listener(self, target: AyakaChannel | None = None):
        '''移除当前频道A对 指定频道B或全部频道 的监听'''
        manager.remove_listener(self.channel, target)

    # ---- 其他 ----
    async def get_user(self, uid: str):
        '''获取当前群组中指定uid的成员信息'''
        if not uid:
            return
        return await bridge.get_member_info(self.channel.id, uid)

    async def get_users(self):
        '''获取当前群组中所有成员信息'''
        return await bridge.get_member_list(self.channel.id)

    async def handle_event(self, event: AyakaEvent):
        '''令manager处理一个事件'''
        return await manager.handle_event(event)


manager = AyakaManager()

# 注册内部服务
bridge.regist(manager.handle_event)
