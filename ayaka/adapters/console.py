'''适配命令行输入输出'''
from typing import Awaitable, Callable
import uvicorn
import asyncio
from fastapi import FastAPI
from loguru import logger
from ..model import AyakaEvent, AyakaSession,  User
from ..cat import bridge
from ..orm import init_orm
from ..helpers import ensure_dir_exists


app: FastAPI = None


def on_startup(func):
    app.on_event("startup")(func)


def init():
    '''初始化'''
    global app
    app = FastAPI()


def run():
    '''运行'''
    uvicorn.run(app=f"{__name__}:app", reload=True)


def clog(text: str):
    logger.opt(colors=True).log("AYAKA", text)


def log(text: str):
    logger.log("AYAKA", text)


async def send(type: str, id: str, msg: str):
    if type == "group":
        clog(f"群聊({id}) <r>Ayaka Bot</r> 说：")
    else:
        clog(f"<r>Ayaka Bot</r> 对私聊({id}) 说：")
    log(msg)


async def send_many(id: str, msgs: list[str]):
    clog(f"群聊({id}) 收到<y>合并转发</y>消息")
    for m in msgs:
        log(m)


def safe_split(text: str,  n: int, sep: str = " "):
    '''安全分割字符串为n部分，不足部分使用空字符串补齐'''
    i = text.count(sep)
    if i < n - 1:
        text += sep * (n - i - 1)
    return text.split(sep, maxsplit=n-1)


class Handler:
    def __init__(self) -> None:
        self.session: AyakaSession = None
        self.uid = 0
        self.func_dict: dict[str, Callable[[str], Awaitable]] = {}

    async def handle_line(self, line: str):
        for k, v in self.func_dict.items():
            if line.startswith(k):
                await v(line[len(k):].strip())
                break

    # def sort_func_dict(self):
    #     items = list(self.func_dict.items())
    #     items.sort(key=lambda x: len(x[0]), reverse=True)
    #     self.func_dict = {k: v for k, v in items}

    def on(self, cmd: str):
        def decorator(func: Callable[[str], Awaitable]):
            self.func_dict[cmd] = func
            # self.sort_func_dict()
            return func
        return decorator


handler = Handler()


@handler.on("#")
async def _(line: str):
    return


@handler.on("p")
async def _(line: str):
    uid, msg = safe_split(line, 2)
    session = AyakaSession(type="private", id=uid)

    handler.uid = uid
    handler.session = session
    name = f"测试{uid}号"
    event = AyakaEvent(
        session=session, msg=msg,
        sender_id=uid, sender_name=name
    )
    clog(f"私聊({uid}) <y>{name}</y> 说：")
    log(msg)
    await bridge.handle_event(event)


@handler.on("g")
async def _(line: str):
    gid, uid, msg = safe_split(line, 3)
    session = AyakaSession(type="group", id=gid)

    handler.uid = uid
    handler.session = session
    name = f"测试{uid}号"
    event = AyakaEvent(
        session=session, msg=msg,
        sender_id=uid, sender_name=name
    )
    clog(f"群聊({gid}) <y>{name}</y>({uid}) 说：")
    log(msg)
    await bridge.handle_event(event)


@handler.on("d")
async def _(line: str):
    try:
        n = float(line)
    except:
        n = 1
    await asyncio.sleep(n)
    print()


@handler.on("s")
async def _(line: str):
    path = ensure_dir_exists(f"script/{line}.txt")
    if not path.exists():
        return

    name = path.stem
    lines = path.read_text(encoding="utf8").split("\n")
    after = "d 0.1"

    for line in lines:
        print(f"{name}>", line)
        if line.startswith("after"):
            after = line[len("after"):].strip()
            continue

        await handler.handle_line(line)
        await handler.handle_line(after)


@handler.on("")
async def _(line: str):
    if handler.session and line:
        uid = handler.uid
        session = handler.session
        name = f"测试{uid}号"
        event = AyakaEvent(
            session=session, msg=line,
            sender_id=uid, sender_name=name
        )
        if session.type == "group":
            gid = session.id
            clog(f"群聊({gid}) <y>{name}</y>({uid}) 说：")
            log(line)
        else:
            clog(f"私聊({uid}) <y>{name}</y> 说：")
            log(line)
        await bridge.handle_event(event)


async def console_loop():
    clog("已接入 <g>Ayaka Console Adapter</g>")
    clog("<y>g</y> \<gid> \<uid> \<msg> | 模拟群聊消息")
    clog("<y>p</y> \<uid> \<msg> | 模拟私聊消息")
    clog("<y>s</y> \<name> | 执行自动化脚本 script/\<name>.txt")
    loop = asyncio.get_running_loop()

    while True:
        line = await loop.run_in_executor(None, input)
        await handler.handle_line(line)


def start_console_loop():
    asyncio.create_task(console_loop())


async def get_member_info(gid: str, uid: str):
    return User(id=uid, name=f"测试{uid}号", role="admin")


async def get_member_list(gid: str):
    return [
        User(id=uid, name=f"测试{uid}号", role="admin")
        for uid in [i+1 for i in range(100)]
    ]


def get_prefix():
    return ""


def get_separate():
    return " "


def regist():
    '''注册服务'''
    if bridge.ready:
        return
    
    # 注册外部服务
    bridge.regist(send)
    bridge.regist(send_many)
    bridge.regist(get_prefix)
    bridge.regist(get_separate)
    bridge.regist(on_startup)
    bridge.regist(get_member_info)
    bridge.regist(get_member_list)

    # 内部服务注册到外部
    on_startup(start_console_loop)

    # 其他初始化
    init_orm()
    logger.level("AYAKA", no=27, icon="⚡")
    
    bridge.ready = True
