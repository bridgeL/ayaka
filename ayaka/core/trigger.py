import asyncio
import re
from typing import TYPE_CHECKING, Awaitable, Callable
from loguru import logger

from .context import get_context, set_context
from .exception import BlockException, NotBlockException
from .database import get_session
from ..helpers import simple_repr, singleton
from ..adapters import get_adapter


if TYPE_CHECKING:
    from .cat import AyakaCat


@singleton
def get_prefixes():
    '''获取命令前缀'''
    return get_adapter().prefixes


@singleton
def get_separate():
    '''获取参数分割符'''
    return get_adapter().separate


class AyakaTrigger:
    def __init__(
        self,
        func: Callable[[], Awaitable],
        cat: "AyakaCat",
        cmd: str,
        state: str,
        sub_state: str,
        always: bool,
        block: bool
    ) -> None:
        self.cmd = cmd
        '''顺便可以区分命令触发和文本触发'''

        self.state = state
        '''顺便可以区分wakeup和state'''

        self.sub_state = sub_state
        self.always = always
        self.block = block
        self.func = func
        self.cat = cat

    @property
    def func_name(self):
        return self.func.__name__

    @property
    def module_name(self):
        return self.func.__module__

    def pre_run(self, prefix):
        context = get_context()

        # 重设一个新的上下文
        context = set_context(context.event)

        # 判定范围
        if context.event.session_type not in self.cat.session_types:
            return False

        # 判断是否被屏蔽
        if not self.cat.valid:
            return False

        # if 命令触发，命令是否符合
        if self.cmd and not context.event.message.startswith(prefix + self.cmd):
            return False

        # 重设超时定时器
        self.cat._refresh_overtime_timer()

        # ---- 一些预处理，并保存到上下文中 ----
        context.trigger = self
        context.cmd = self.cmd

        # 创建数据库会话
        context.db_session = get_session()
        context.wait_tasks = []

        # 只有在有命令的情况下才剥离命令
        if self.cmd:
            n = len(prefix+self.cmd)
        else:
            n = 0

        separate = get_separate()

        # 剥离命令
        context.arg = context.event.message[n:].strip(separate)

        # 分割
        context.args = [arg for arg in context.arg.split(separate) if arg]

        # 提取整数（包含负数）
        pt = re.compile(r"^-?\d+$")
        context.nums = [int(arg) for arg in context.args if pt.search(arg)]
        # ---- 一些预处理，并保存到上下文中 ----

        return True

    async def run(self):
        # 预检查并做一些预处理
        for prefix in get_prefixes():
            if self.pre_run(prefix):
                break
        else:
            return False

        # 打印日志
        items = [
            f"<y>适配器</y> {get_adapter().name}",
            f"<y>猫猫</y> {self.cat.name}"
        ]
        if self.cmd:
            items.append(f"<y>命令</y> {self.cmd}")
        else:
            items.append("<g>文字</g>")
        if self.state:
            items.append(f"<c>状态</c> {self.state}")
        if self.sub_state:
            items.append(f"<c>子状态</c> {self.sub_state}")
        items.append(f"<y>回调</y> {self.func_name}")
        logger.opt(colors=True).debug(" | ".join(items))

        # 运行函数
        try:
            await self.func()
        except BlockException:
            logger.info("BlockException")
            return True
        except NotBlockException:
            logger.info("NotBlockException")
            return False

        context = get_context()
        while context.wait_tasks:
            ts = context.wait_tasks
            context.wait_tasks = []
            await asyncio.gather(*ts)
        
        # ---- 待修改
        context.db_session.commit()
        # 必须关，否则内存泄漏
        context.db_session.close()

        # 返回是否阻断
        return self.block

    def __repr__(self) -> str:
        return simple_repr(
            self,
            cat=self.cat.name,
            func=self.func_name,
            module=self.module_name
        )
