'''适配 nonebot2机器人 onebot v11适配器'''
import uvicorn
from math import ceil
import nonebot
from nonebot.matcher import current_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment, Adapter
from ..model import AyakaEvent, User, AyakaSession
from ..cat import bridge
from ..orm import init_orm


app = None


def init():
    '''初始化'''
    global app
    nonebot.init()
    app = nonebot.get_app()
    driver = nonebot.get_driver()
    driver.register_adapter(Adapter)


def run():
    '''运行'''
    uvicorn.run(app=f"{__name__}:app", reload=True)


async def handle_msg(bot: Bot, event: MessageEvent):
    # 处理消息，保留text、at和to_me
    ms: list[str] = []
    for m in event.message:
        if m.type == "text":
            ms.append(str(m))
        elif m.type == "at":
            ms.append(str(m.data["qq"]))
    if event.to_me:
        ms.append(bot.self_id)
    msg = bridge.get_separate().join(ms)

    # 组成ayaka事件
    sid = event.group_id if event.message_type == "group" else event.user_id
    ayaka_event = AyakaEvent(
        session=AyakaSession(type=event.message_type, id=sid),
        msg=msg,
        sender_id=event.sender.user_id,
        sender_name=event.sender.card or event.sender.nickname,
    )
    await bridge.handle_event(ayaka_event)


def get_current_bot() -> Bot:
    return current_bot.get()


async def send(type: str, id: str, msg: str):
    bot = get_current_bot()
    if type == "group":
        await bot.send_group_msg(group_id=int(id), message=msg)
    else:
        await bot.send_private_msg(user_id=int(id), message=msg)


async def send_many(id: str, msgs: list[str]):
    bot = get_current_bot()
    # 分割长消息组（不可超过100条
    div_len = 100
    div_cnt = ceil(len(msgs) / div_len)
    for i in range(div_cnt):
        msgs = [
            MessageSegment.node_custom(
                user_id=int(bot.self_id),
                nickname="Ayaka Bot",
                content=str(m)
            )
            for m in msgs[i*div_len: (i+1)*div_len]
        ]
        await bot.send_group_forward_msg(group_id=int(id), messages=msgs)


async def get_member_info(gid: str, uid: str):
    bot = get_current_bot()
    try:
        user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
        return User(id=user["user_id"], name=user["card"] or user["nickname"], role=user["role"])
    except:
        pass


async def get_member_list(gid: str):
    bot = get_current_bot()
    try:
        users = await bot.get_group_member_list(group_id=int(gid))
        return [
            User(
                id=user["user_id"],  role="admin",
                name=user["card"] or user["nickname"],
            )
            for user in users
        ]
    except:
        pass


def regist():
    '''注册服务'''
    if bridge.ready:
        return

    driver = nonebot.get_driver()
    prefix = list(driver.config.command_start)[0]
    separate = list(driver.config.command_sep)[0]

    def get_prefix():
        return prefix

    def get_separate():
        return separate

    # 注册外部服务
    bridge.regist(send)
    bridge.regist(send_many)
    bridge.regist(get_prefix)
    bridge.regist(get_separate)
    bridge.regist(driver.on_startup)
    bridge.regist(get_member_info)
    bridge.regist(get_member_list)

    # 内部服务注册到外部
    nonebot.on_message(handlers=[handle_msg])

    # 其他初始化
    init_orm()

    bridge.ready = True
