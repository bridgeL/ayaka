'''适配命令行输入输出'''
import re
from loguru import logger
import uvicorn
import asyncio
from fastapi import FastAPI
from typing import Awaitable, Callable

from .adapter import AyakaAdapter
from .model import GroupMemberInfo, AyakaEvent
from .detect import is_hoshino, is_nb1, is_nb2ob11
from ..helpers import ensure_dir_exists
from ..logger import ayaka_log, ayaka_clog


at_pt = re.compile(r"@([^ ]+?)(?= |$)")


class ConsoleAdapter(AyakaAdapter):
    '''console 适配器'''

    def first_init(self) -> None:
        '''在第一次初始化时执行'''
        handler.handle_event = self.handle_event
        self.on_startup(start_loop)

    async def send_group(self, id: str, msg: str) -> bool:
        '''发送消息到指定群聊'''
        ayaka_clog(f"群聊({id}) <r>Ayaka Bot</r> 说：")
        print(msg)
        return True

    async def send_private(self, id: str, msg: str) -> bool:
        '''发送消息到指定私聊'''
        ayaka_clog(f"<r>Ayaka Bot</r> 对私聊({id}) 说：")
        print(msg)
        return True

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
        '''发送消息组到指定群聊'''
        ayaka_clog(f"群聊({id}) 收到<y>合并转发</y>消息")
        print("\n\n".join(msgs))
        return True

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
        return GroupMemberInfo(id=uid, name=f"测试{uid}号", role="admin")

    async def get_group_members(self, gid: str) -> list[GroupMemberInfo]:
        '''获取群内所有用户的信息'''
        return [
            GroupMemberInfo(id=uid, name=f"测试{uid}号", role="admin")
            for uid in [i+1 for i in range(100)]
        ]

    def on_startup(self, async_func: Callable[[], Awaitable]):
        '''asgi服务启动后钩子，注册回调必须是异步函数'''
        async def _func():
            try:
                await async_func()
            except:
                logger.exception("asgi服务启动后钩子发生错误")
        on_startup(_func)


ConsoleAdapter.name = "console"
ConsoleAdapter.prefixes = [""]


class Handler:
    def __init__(self) -> None:
        self.session_type = "group"
        self.session_id = 100
        self.sender_id = 1
        self.sender_name = "测试1号"
        self.func_dict: dict[str, Callable[[str], Awaitable]] = {}
        self.handle_event = None

    async def handle_line(self, line: str):
        for cmd, func in self.func_dict.items():
            if line.startswith(cmd):
                await func(line[len(cmd):].strip())
                break

    def on(self, cmd: str):
        def decorator(func: Callable[[str], Awaitable]):
            self.func_dict[cmd] = func
            return func
        return decorator

    def handle_msg(self, msg: str):
        name = self.sender_name
        uid = self.sender_id

        if self.session_type == "group":
            gid = self.session_id
            ayaka_clog(f"群聊({gid}) <y>{name}</y>({uid}) 说：")
        else:
            ayaka_clog(f"私聊({uid}) <y>{name}</y> 说：")

        ayaka_log(msg)

        at = None
        for r in at_pt.finditer(msg):
            at = r.group(1)
            msg = msg[:r.start()]+msg[r.end():]
            break

        ayaka_event = AyakaEvent(
            session_type=self.session_type,
            session_id=self.session_id,
            sender_id=uid,
            sender_name=name,
            message=msg,
            at=at
        )

        asyncio.create_task(self.handle_event(ayaka_event))


async def start_loop():
    asyncio.create_task(console_loop())


def safe_split(text: str,  n: int, sep: str = " "):
    '''安全分割字符串为n部分，不足部分使用空字符串补齐'''
    i = text.count(sep)
    if i < n - 1:
        text += sep * (n - i - 1)
    return text.split(sep, maxsplit=n-1)


if is_hoshino() or is_nb1():
    import nonebot
    app = nonebot.get_bot().asgi
    on_startup = nonebot.get_bot().on_startup
elif is_nb2ob11():
    import nonebot
    app = nonebot.get_asgi()
    on_startup = nonebot.get_driver().on_startup
else:
    app = FastAPI()
    on_startup = app.on_event("startup")

handler = Handler()


async def console_loop():
    ayaka_clog("已接入 <g>Ayaka Console Adapter</g>")
    await show_help("")
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, input)
        await handler.handle_line(line)


@handler.on("#")
async def _(line: str):
    pass


@handler.on("p ")
async def _(line: str):
    uid, msg = safe_split(line, 2)
    handler.sender_id = uid
    handler.sender_name = f"测试{uid}号"
    handler.session_type = "private"
    handler.session_id = uid
    if msg:
        handler.handle_msg(msg)


@handler.on("g ")
async def _(line: str):
    gid, uid, msg = safe_split(line, 3)
    handler.sender_id = uid
    handler.sender_name = f"测试{uid}号"
    handler.session_type = "group"
    handler.session_id = gid
    if msg:
        handler.handle_msg(msg)


@handler.on("d ")
async def _(line: str):
    try:
        n = float(line)
    except:
        n = 1
    await asyncio.sleep(n)
    print()


@handler.on("s ")
async def _(line: str):
    path = ensure_dir_exists(f"script/{line}.txt")
    if not path.exists():
        return ayaka_log(f"脚本不存在 {path}")
    ayaka_log(f"执行脚本 {path}")

    name = path.stem
    lines = path.read_text(encoding="utf8").split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    after = "d 0.1"

    for line in lines:
        print(f"{name}>", line)
        if line.startswith("after"):
            after = line[len("after"):].strip()
            continue

        await handler.handle_line(line)
        await handler.handle_line(after)


@handler.on("h")
async def show_help(line: str):
    if line.strip():
        return await deal_line(f"h{line}")
    ayaka_clog("<y>g</y> \<gid> \<uid> \<msg> | 模拟群聊消息")
    ayaka_clog("<y>p</y> \<uid> \<msg> | 模拟私聊消息")
    ayaka_clog("<y>d</y> \<n> | 延时n秒")
    ayaka_clog("<y>s</y> \<name> | 执行测试脚本 script/\<name>.txt")
    ayaka_clog("<y>h</y> | 查看帮助")


@handler.on("")
async def deal_line(msg: str):
    if msg:
        handler.handle_msg(msg)


def run():
    '''运行'''
    uvicorn.run(app=f"{__name__}:app", reload=True)
