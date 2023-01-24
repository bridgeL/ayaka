'''适配命令行输入输出'''
import re
import uvicorn
import asyncio
from loguru import logger
from fastapi import FastAPI
from typing import Awaitable, Callable
from ..logger import ayaka_log, ayaka_clog
from ..event import AyakaEvent
from ..bridge import bridge, GroupMemberInfo
from ..helpers import ensure_dir_exists


pt = re.compile(r"@([^ ]+?)(?= |$)")


async def handle_event(ayaka_event: AyakaEvent) -> None:
    try:
        await bridge.handle_event(ayaka_event)
    except:
        logger.exception(f"ayaka 处理事件（{ayaka_event}）时发生错误")


class Handler:
    def __init__(self) -> None:
        self.session_type = "group"
        self.session_id = 0
        self.sender_id = 0
        self.sender_name = ""
        self.func_dict: dict[str, Callable[[str], Awaitable]] = {}

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
        for r in pt.finditer(msg):
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

        asyncio.create_task(handle_event(ayaka_event))


handler = Handler()
app = FastAPI()


def on_startup(func):
    app.on_event("startup")(func)


async def send_group(id: str, msg: str) -> bool:
    ayaka_clog(f"群聊({id}) <r>Ayaka Bot</r> 说：")
    print(msg)
    return True


async def send_private(id: str, msg: str) -> bool:
    ayaka_clog(f"<r>Ayaka Bot</r> 对私聊({id}) 说：")
    print(msg)
    return True


async def send_group_many(id: str, msgs: list[str]) -> bool:
    ayaka_clog(f"群聊({id}) 收到<y>合并转发</y>消息")
    print("\n\n".join(msgs))
    return True


def safe_split(text: str,  n: int, sep: str = " "):
    '''安全分割字符串为n部分，不足部分使用空字符串补齐'''
    i = text.count(sep)
    if i < n - 1:
        text += sep * (n - i - 1)
    return text.split(sep, maxsplit=n-1)


async def console_loop():
    ayaka_clog("已接入 <g>Ayaka Console Adapter</g>")
    await show_help("")
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, input)
        await handler.handle_line(line)


async def start_console_loop():
    asyncio.create_task(console_loop())


async def get_member_info(gid: str, uid: str):
    return GroupMemberInfo(id=uid, name=f"测试{uid}号", role="admin")


async def get_member_list(gid: str):
    return [
        GroupMemberInfo(id=uid, name=f"测试{uid}号", role="admin")
        for uid in [i+1 for i in range(100)]
    ]


def get_prefixes():
    return [""]


def get_separates():
    return [" "]


# 注册外部服务
bridge.regist(send_group)
bridge.regist(send_private)
bridge.regist(send_group_many)
bridge.regist(get_prefixes)
bridge.regist(get_separates)
bridge.regist(get_member_info)
bridge.regist(get_member_list)
bridge.regist(on_startup)

# 内部服务注册到外部
on_startup(start_console_loop)


@ handler.on("#")
async def _(line: str):
    pass


@ handler.on("p ")
async def _(line: str):
    uid, msg = safe_split(line, 2)
    handler.sender_id = uid
    handler.sender_name = f"测试{uid}号"
    handler.session_type = "private"
    handler.session_id = uid
    if msg:
        handler.handle_msg(msg)


@ handler.on("g ")
async def _(line: str):
    gid, uid, msg = safe_split(line, 3)
    handler.sender_id = uid
    handler.sender_name = f"测试{uid}号"
    handler.session_type = "group"
    handler.session_id = gid
    if msg:
        handler.handle_msg(msg)


@ handler.on("d ")
async def _(line: str):
    try:
        n = float(line)
    except:
        n = 1
    await asyncio.sleep(n)
    print()


@ handler.on("s ")
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


@ handler.on("h")
async def show_help(line: str):
    if line.strip():
        return await deal_line(f"h{line}")
    ayaka_clog("<y>g</y> \<gid> \<uid> \<msg> | 模拟群聊消息")
    ayaka_clog("<y>p</y> \<uid> \<msg> | 模拟私聊消息")
    ayaka_clog("<y>d</y> \<n> | 延时n秒")
    ayaka_clog("<y>s</y> \<name> | 执行测试脚本 script/\<name>.txt")
    ayaka_clog("<y>h</y> | 查看帮助")


@ handler.on("")
async def deal_line(msg: str):
    if not handler.session_id or not handler.sender_id:
        return ayaka_log("请先设置默认角色（发出第一条模拟消息后自动设置）")
    if msg:
        handler.handle_msg(msg)


def run():
    '''运行'''
    uvicorn.run(app=f"{__name__}:app", reload=True)
