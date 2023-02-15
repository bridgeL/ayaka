import re
import asyncio
from loguru import logger
from typing import TYPE_CHECKING, Awaitable, Callable
from .exception import BlockException, NotBlockException
from .helpers import simple_repr
from .adapters import get_adapter
from .config import get_root_config
from .context import ayaka_context

if TYPE_CHECKING:
    from .cat import AyakaCat


class AyakaTrigger:
    def __init__(
        self,
        func: Callable[[], Awaitable],
        cat: "AyakaCat",
        cmd: str,
        state: str,
        sub_state: str,
        block: bool
    ) -> None:
        self.cmd = cmd
        '''顺便可以区分命令触发和文本触发'''

        self.state = state
        '''顺便可以区分wakeup和state'''

        self.sub_state = sub_state
        self.block = block
        self.func = func
        self.cat = cat

    @property
    def func_name(self):
        return self.func.__name__

    @property
    def module_name(self):
        return self.func.__module__

    def pre_check(self, prefix):
        context = ayaka_context

        # 判定范围
        if context.event.session_type not in self.cat.session_types:
            return False

        # if 命令触发，命令是否符合
        if self.cmd and not context.event.message.startswith(prefix + self.cmd):
            return False

        # 重设超时定时器
        self.cat._refresh_overtime_timer()

        # ---- 一些预处理，并保存到上下文中 ----
        context.trigger = self
        context.cmd = self.cmd

        # 只有在有命令的情况下才剥离命令
        if self.cmd:
            n = len(prefix+self.cmd)
        else:
            n = 0

        separate = get_root_config().separate

        # 剥离命令
        context.arg = context.event.message[n:].strip(separate)

        # 分割
        context.args = [arg for arg in context.arg.split(separate) if arg]

        # 提取整数（包含负数）
        pt = re.compile(r"^-?\d+$")
        context.nums = [int(arg) for arg in context.args if pt.search(arg)]

        return True

    async def run(self):
        # 预检查并做一些预处理
        for prefix in get_root_config().prefixes:
            if self.pre_check(prefix):
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
        finally:
            context = ayaka_context
            while context.wait_tasks:
                ts = context.wait_tasks
                context.wait_tasks = []
                await asyncio.gather(*ts)

            # ---- 待修改
            # 必须关，否则内存泄漏
            if context.db_session_flag:
                context.db_session.commit()
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
