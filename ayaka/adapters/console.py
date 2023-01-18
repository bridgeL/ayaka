'''适配命令行输入输出'''
import re
from typing import Awaitable, Callable
import uvicorn
import asyncio
from fastapi import FastAPI
from ..logger import ayaka_log, ayaka_clog
from ..model import AyakaEvent, AyakaChannel, AyakaSender, GroupMember
from ..cat import bridge
from ..helpers import ensure_dir_exists

pt = re.compile(r"@([^ ]+?)(?= |$)")


class Handler:
    def __init__(self) -> None:
        self.channel: AyakaChannel = None
        self.sender: AyakaSender = None
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
        name = self.sender.name
        uid = self.sender.id

        if self.channel.type == "group":
            gid = self.channel.id
            ayaka_clog(f"群聊({gid}) <y>{name}</y>({uid}) 说：")
        else:
            ayaka_clog(f"私聊({uid}) <y>{name}</y> 说：")

        ayaka_log(msg)

        at = None
        for r in pt.finditer(msg):
            at = r.group(1)
            msg = msg[:r.start()]+msg[r.end():]
            break

        asyncio.create_task(bridge.handle_event(AyakaEvent(
            channel=self.channel,
            sender=self.sender,
            message=msg,
            at=at,
        )))


handler = Handler()
app = FastAPI()


def on_startup(func):
    app.on_event("startup")(func)


async def send(type: str, id: str, msg: str):
    if type == "group":
        ayaka_clog(f"群聊({id}) <r>Ayaka Bot</r> 说：")
    else:
        ayaka_clog(f"<r>Ayaka Bot</r> 对私聊({id}) 说：")
    ayaka_log(msg)


async def send_many(id: str, msgs: list[str]):
    ayaka_clog(f"群聊({id}) 收到<y>合并转发</y>消息")
    for m in msgs:
        ayaka_log(m)


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
    return GroupMember(id=uid, name=f"测试{uid}号", role="admin")


async def get_member_list(gid: str):
    return [
        GroupMember(id=uid, name=f"测试{uid}号", role="admin")
        for uid in [i+1 for i in range(100)]
    ]


def get_prefixes():
    return [""]


def get_separates():
    return [" "]


# 注册外部服务
bridge.regist(send)
bridge.regist(send_many)
bridge.regist(get_prefixes)
bridge.regist(get_separates)
bridge.regist(get_member_info)
bridge.regist(get_member_list)
bridge.regist(on_startup)

# 内部服务注册到外部
on_startup(start_console_loop)


@handler.on("#")
async def _(line: str):
    pass


@handler.on("p ")
async def _(line: str):
    uid, msg = safe_split(line, 2)
    handler.sender = AyakaSender(id=uid, name=f"测试{uid}号")
    handler.channel = AyakaChannel(type="private", id=uid)
    if msg:
        handler.handle_msg(msg)


@handler.on("g ")
async def _(line: str):
    gid, uid, msg = safe_split(line, 3)
    handler.sender = AyakaSender(id=uid, name=f"测试{uid}号")
    handler.channel = AyakaChannel(type="group", id=gid)
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
    if not (handler.channel and handler.sender and msg):
        return ayaka_log("请先设置默认角色（发出第一条模拟消息后自动设置）")
    handler.handle_msg(msg)


def run():
    '''运行'''
    uvicorn.run(app=f"{__name__}:app", reload=True)
