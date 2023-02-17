'''适配命令行输入输出'''
import re
import asyncio
from io import TextIOWrapper
from fastapi import FastAPI
from typing import Awaitable, Callable, Optional
from ayaka_utils import ensure_dir_exists, singleton

from .adapter import GroupMemberInfo, AyakaEvent, AyakaAdapter, regist, get_first_adapter
from ..logger import ayaka_log, ayaka_clog


at_pt = re.compile(r"@([^ ]+?)(?= |$)")
app = None


class Handler:
    def __init__(self) -> None:
        self.session_type = "group"
        self.session_id = 100
        self.sender_id = 1
        self.sender_name = "测试1号"
        self.func_dict: dict[str, Callable[[str], Awaitable]] = {}
        self.handle_event = None
        self.outpath: Optional[TextIOWrapper] = None

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
        raw_msg = msg
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
            at=at,
            raw_message=raw_msg
        )

        asyncio.create_task(self.handle_event(ayaka_event))

    def print(self, *args, **kwargs):
        print(*args, **kwargs)
        if self.outpath:
            kwargs["file"] = self.outpath
            print(*args, **kwargs)
            self.outpath.flush()


def safe_split(text: str,  n: int, sep: str = " "):
    '''安全分割字符串为n部分，不足部分使用空字符串补齐'''
    i = text.count(sep)
    if i < n - 1:
        text += sep * (n - i - 1)
    return text.split(sep, maxsplit=n-1)


handler = Handler()


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
    handler.print()


@handler.on("s ")
async def _(line: str):
    if ">" in line:
        in_, out = line.split(">")
        in_ = in_.strip()
        out = out.strip()

        if in_ == out:
            print("输入输出文件不可相同")
            return

        if not out:
            out = f"{in_}_output"

        inpath = ensure_dir_exists(f"script/{in_}.txt")
        outpath = ensure_dir_exists(f"script/{out}.txt")
        handler.outpath = outpath.open("w+")
        flag = True
    else:
        inpath = ensure_dir_exists(f"script/{line}.txt")
        flag = False

    if not inpath.exists():
        return ayaka_log(f"脚本不存在 {inpath}")
    ayaka_log(f"执行脚本 {inpath}")

    name = inpath.stem
    lines = inpath.read_text(encoding="utf8").split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    after = "d 0.1"

    for line in lines:
        handler.print(f"{name}>", line)
        if line.startswith("after"):
            after = line[len("after"):].strip()
            continue

        await handler.handle_line(line)
        await handler.handle_line(after)

    if flag:
        handler.outpath = None


@handler.on("h")
async def show_help(line: str):
    if line.strip():
        return await deal_line(f"h{line}")

    items = [
        "<y>g</y> \<gid> \<uid> \<msg> | 模拟群聊消息",
        "<y>p</y> \<uid> \<msg> | 模拟私聊消息",
        "<y>d</y> 2.3 | 延时2.3秒",
        "<y>s</y> a > b | 执行测试脚本 script/a.txt 将结果写入 script/b.txt",
        "<y>h</y> | 查看帮助"
    ]
    for item in items:
        ayaka_clog(item)


@handler.on("")
async def deal_line(msg: str):
    if msg:
        handler.handle_msg(msg)


@singleton
class ConsoleAdapter(AyakaAdapter):
    '''console 适配器'''

    def __init__(self) -> None:
        first_adapter = get_first_adapter()
        if first_adapter:
            self.asgi = first_adapter.asgi
            self.on_startup = first_adapter.on_startup
            self.on_startup = first_adapter.on_shutdown
        else:
            self.asgi = FastAPI()
            self._on_startup = self.asgi.on_event("startup")
            self._on_shutdown = self.asgi.on_event("shutdown")

        global app
        app = self.asgi

        handler.handle_event = self.handle_event

        async def start_loop():
            asyncio.create_task(console_loop())

        async def console_loop():
            ayaka_clog("已接入 <g>Ayaka Console Adapter</g>")
            await show_help("")
            loop = asyncio.get_running_loop()
            while True:
                line = await loop.run_in_executor(None, input)
                await handler.handle_line(line)

        self.on_startup(start_loop)

    async def send_group(self, id: str, msg: str) -> bool:
        '''发送消息到指定群聊'''
        ayaka_clog(f"群聊({id}) <r>Ayaka Bot</r> 说：")
        handler.print(msg)
        return True

    async def send_private(self, id: str, msg: str) -> bool:
        '''发送消息到指定私聊'''
        ayaka_clog(f"<r>Ayaka Bot</r> 对私聊({id}) 说：")
        handler.print(msg)
        return True

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
        '''发送消息组到指定群聊'''
        ayaka_clog(f"群聊({id}) 收到<y>合并转发</y>消息")
        handler.print("\n\n".join(msgs))
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


ConsoleAdapter.name = "console"
regist(ConsoleAdapter)


def run(**kwargs):
    '''运行'''
    import uvicorn
    kwargs.setdefault("app", f"{__name__}:app")
    kwargs.setdefault("reload", True)
    uvicorn.run(**kwargs)
