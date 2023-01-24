import asyncio
import inspect
from typing import Awaitable, Callable, TypeVar

from .logger import clogger
from .helpers import ensure_list
from .context import get_context
from .session import get_session_cls, AyakaSession, AyakaGroup, AyakaPrivate
from .bridge import bridge
from .manager import manager
from .event import AyakaEvent
from .config import root_config
from .trigger import AyakaTrigger


T = TypeVar("T")
'''任意类型'''


STD = dict[str, dict[str, list[AyakaTrigger]]]
'''状态触发字典'''


class AyakaCat:
    def __init__(
        self,
        name: str,
        overtime: int = 600,
        group: bool = True,
        private: bool = False,
    ) -> None:
        '''创建猫猫

        参数：

            name：猫猫名字

            overtime：超时未收到指令则自动关闭，单位：秒，<=0则禁止该特性
        '''
        self.name = name
        manager.add_cat(self)

        self.module_path = inspect.stack()[1].filename
        '''模块地址'''

        self.sessions: list[AyakaSession] = []
        '''所有会话'''

        self.always_triggers: list[AyakaTrigger] = []
        '''总是触发'''

        self.state_trigger_dict: STD = {}
        '''状态触发'''

        items = []
        if group:
            items.append("group")
        if private:
            items.append("private")

        self.session_types = items
        '''可响应的会话范围'''

        self.overtime = overtime
        '''超时限制'''

        self._intro = ""
        '''猫猫介绍'''

        self._helps: dict[str, list] = {}
        '''自动猫猫帮助'''

        self._invalid_list = root_config.block_cat_dict.get(name, [])
        '''被各个会话的屏蔽情况'''

    # ---- 超时控制 ----
    @property
    def _future(self):
        '''当前会话状态'''
        return self.session._future

    @_future.setter
    def _future(self, v):
        self.session._future = v

    def _start_overtime_timer(self):
        '''启动超时定时器'''
        if self.overtime > 0:
            loop = asyncio.get_event_loop()
            self._future = loop.create_future()
            loop.create_task(self._overtime_handle())

    def _refresh_overtime_timer(self):
        '''重置超时定时器'''
        if self._stop_overtime_timer():
            self._start_overtime_timer()

    async def _overtime_handle(self):
        try:
            await asyncio.wait_for(self._future, self.overtime)
        except asyncio.exceptions.TimeoutError:
            await self.send("猫猫超时")
            await self.rest()

    def _stop_overtime_timer(self):
        '''停止超时定时器'''
        if not self._future:
            return False
        if self._future.done():
            return False
        if self._future.cancelled():
            return False

        self._future.set_result(True)
        return True

    # ---- valid ----
    @property
    def valid(self):
        '''当前猫猫是否可用'''
        return self.session.mark not in self._invalid_list

    @valid.setter
    def valid(self, value: bool):
        '''设置当前猫猫是否可用'''
        change_flag = False
        if value and not self.valid:
            self._invalid_list.remove(self.session.mark)
            change_flag = True

        elif not value and self.valid:
            self._invalid_list.append(self.session.mark)
            change_flag = True

        if change_flag:
            if self._invalid_list:
                root_config.block_cat_dict[self.name] = self._invalid_list
            else:
                root_config.block_cat_dict.pop(self.name, None)
            root_config.save()

    # ---- 会话 ----
    @property
    def session_type(self):
        return self.event.session_type

    @property
    def session(self):
        '''当前会话'''
        st = self.event.session_type
        sid = self.event.session_id
        for s in self.sessions:
            if s.__session_type__ == st and s.id == sid:
                return s

        cls = get_session_cls(st)
        s = cls(id=sid)
        self.sessions.append(s)
        return s

    @property
    def group(self):
        '''当前群聊会话'''
        s = self.session
        if isinstance(s, AyakaGroup):
            return s

    @property
    def private(self):
        '''当前私聊会话'''
        s = self.session
        if isinstance(s, AyakaPrivate):
            return s

    @property
    def group_member(self):
        '''当前群聊会话·群成员子会话'''
        if self.session_type == "group":
            return self.group.member

    @property
    def user(self):
        '''当前用户'''
        return self.group_member or self.private or self.session

    # ---- 上下文 ----
    @property
    def context(self):
        '''当前上下文'''
        return get_context()

    @property
    def event(self):
        '''当前事件'''
        return self.context.event

    @property
    def message(self):
        '''当前消息'''
        return self.event.message

    @property
    def trigger(self):
        '''当前触发器'''
        return self.context.trigger

    @property
    def cmd(self):
        '''当前触发命令'''
        return self.context.cmd

    @property
    def arg(self):
        '''当前消息移除命令后的内容'''
        return self.context.arg

    @property
    def args(self):
        '''当前消息移除命令后的内容进一步分割'''
        return self.context.args

    @property
    def nums(self):
        '''当前消息中的的整数数字'''
        return self.context.nums

    # ---- on_xxx ----
    def on_cmd(
        self,
        *,
        cmds: str | list[str] = "",
        states: str | list[str] = "",
        sub_states: str | list[str] = "",
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
        sub_states = ensure_list(sub_states)

        def decorator(func: Callable[[], Awaitable]):
            if auto_help:
                self._add_help(cmds, states, func)

            for cmd in cmds:
                for state in states:
                    for sub_state in sub_states:
                        trigger = AyakaTrigger(
                            func=func,
                            cat=self,
                            cmd=cmd,
                            state=state,
                            sub_state=sub_state,
                            always=always,
                            block=block,
                        )
                        self.add_state_trigger(trigger, state, sub_state)

            items = [f"<y>猫猫</y> {self.name}"]
            if cmds != [""]:
                items.append(f"<y>命令</y> {cmds}")
            else:
                items.append("<g>文字</g>")
            if states != [""]:
                items.append(f"<c>状态</c> {states}")
            if sub_states != [""]:
                items.append(f"<c>子状态</c> {sub_states}")
            items.append(f"<y>回调</y> {func.__name__}")

            clogger.trace(f" | ".join(items))
            return func
        return decorator

    def on_text(
        self,
        *,
        states: str | list[str] = "",
        sub_states: str | list[str] = "",
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
        return self.on_cmd(states=states, always=always, block=block, auto_help=auto_help, sub_states=sub_states)

    # ---- 猫猫帮助 ----
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

    # ---- 状态 ----
    @property
    def state(self):
        '''当前会话状态'''
        return self.session.state

    @state.setter
    def state(self, v):
        self.session.state = v
        self._refresh_overtime_timer()

    @property
    def sub_state(self):
        return self.user.state

    @sub_state.setter
    def sub_state(self, v):
        self.user.state = v
        self._refresh_overtime_timer()

    async def wakeup(self, state: str = "idle"):
        '''唤醒猫猫，唤醒后猫猫状态默认为idle

        参数: 

            state: 新状态
        '''
        if not self.state:
            self._start_overtime_timer()
            self.state = state
            await self.send(f"已唤醒猫猫[{self.name}]")

    async def rest(self):
        '''猫猫休息'''
        if self.state:
            self.state = ""
            await self.send(f"[{self.name}]猫猫休息了")
            self._stop_overtime_timer()

    # ---- 基本发送 ----
    async def send_group(self, id: str, msg: str):
        '''基本发送方法 发送消息至指定群聊'''
        self._refresh_overtime_timer()
        return await bridge.send_group(id, msg)

    async def send_private(self, id: str, msg: str):
        '''基本发送方法 发送消息至指定私聊'''
        self._refresh_overtime_timer()
        return await bridge.send_private(id, msg)

    async def send_group_many(self, id: str, msgs: list[str]):
        '''基本发送方法 发送消息组至指定群聊'''
        self._refresh_overtime_timer()
        return await bridge.send_group_many(id, msgs)

    # ---- 快捷发送 ----
    async def send(self, msg: str):
        '''发送消息至当前会话'''
        if self.session_type == "group":
            return await self.send_group(id=self.session.id, msg=msg)
        return await self.send_private(id=self.session.id, msg=msg)

    async def send_many(self, msgs: list[str]):
        '''发送消息组至当前会话'''
        if self.session_type == "group":
            return await self.send_group_many(id=self.session.id, msgs=msgs)
        return await self.send_private(id=self.session.id, msg="\n".join(msgs))

    async def send_help(self):
        '''发送自身帮助'''
        await self.send(self.help)

    # ---- cache ----
    @property
    def cache(self):
        '''当前会话缓存数据'''
        return self.session.cache

    def pop_data(self, factory: Callable[[], T]) -> T:
        '''弹出缓存数据

        参数:

            factory: 无参数的同步函数（类也可以）
        '''
        return self.session.pop_data(factory)

    def get_data(self, factory: Callable[[], T]) -> T:
        '''获取缓存数据

        参数:

            factory: 无参数的同步函数（类也可以）
        '''
        return self.session.get_data(factory)

    # ---- 快捷命令 ----
    def set_wakeup_cmds(self, cmds: str | list[str]):
        '''设置唤醒命令'''
        @self.on_cmd(cmds=cmds)
        async def wakeup():
            '''唤醒猫猫'''
            await self.wakeup()
            await self.send_help()
        wakeup.__module__ = self.module_path

    def set_rest_cmds(self, cmds: str | list[str]):
        '''设置休息命令'''
        @self.on_cmd(cmds=cmds, states="*")
        async def rest():
            '''猫猫休息'''
            await self.rest()
        rest.__module__ = self.module_path

    # ---- 私聊消息监听 ----
    def add_private_redirect(self, private_id: str):
        '''添加当前群聊A对指定私聊B的监听，当B收到消息后，会转发一份副本给A处理'''
        if self.session_type == "group":
            manager.add_private_redirect(self.group.id, private_id)

    def remove_private_redirect(self,  private_id: str = ""):
        '''移除当前群聊A对 指定私聊B或全部私聊 的监听'''
        if self.session_type == "group":
            manager.remove_private_redirect(self.group.id, private_id)

    # ---- trigger ----
    def add_always_trigger(self, trigger: "AyakaTrigger"):
        '''添加总是触发'''
        self.always_triggers.append(trigger)
        self.always_triggers.sort(key=lambda t: len(t.cmd), reverse=True)

    def add_state_trigger(self, trigger: AyakaTrigger, state: str, sub_state: str = "*"):
        '''添加状态触发'''
        std = self.state_trigger_dict
        std.setdefault(state, {})
        std[state].setdefault(sub_state, [])
        std[state][sub_state].append(trigger)
        std[state][sub_state].sort(key=lambda t: len(t.cmd), reverse=True)

    async def handle_event(self, event: AyakaEvent):
        '''处理事件'''

        # 设置上下文
        context = get_context()
        context.event = event

        state = self.state
        sub_state = self.sub_state

        # 触发器列表
        ts = [
            *self.always_triggers,
            *self.state_trigger_dict.get("*", {}).get("*", []),
            *self.state_trigger_dict.get("*", {}).get(sub_state, []),
            *self.state_trigger_dict.get(state, {}).get("*", []),
            *self.state_trigger_dict.get(state, {}).get(sub_state, []),
        ]
        
        # 遍历尝试执行
        for t in ts:
            if await t.run():
                return

    # ---- 其他 ----
    async def get_user(self, uid: str):
        '''获取当前群组中指定uid的成员信息'''
        if uid and self.session_type == "group":
            return await bridge.get_member_info(self.group.id, uid)

    async def get_users(self):
        '''获取当前群组中所有成员信息'''
        if self.session_type == "group":
            return await bridge.get_member_list(self.group.id)
