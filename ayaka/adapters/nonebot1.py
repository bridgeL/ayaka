'''适配 hoshino机器人'''
from math import ceil
from nonebot import NoneBot
from aiocqhttp import Event as CQEvent
from ..bridge import bridge
from ..model import AyakaEvent, AyakaSession, User
from ..helpers import singleton
from ..orm import start_loop


def format_msg(message):
    '''处理消息，保留text、at'''
    ms: list[str] = []
    for m in message:
        if m.type == "text":
            ms.append(str(m))
        elif m.type == "at":
            ms.append(str(m.data["qq"]))
    return bridge.get_separate().join(ms)


async def handle_msg(ev: CQEvent):
    msg = format_msg(ev.message)

    # 组成ayaka事件
    stype = ev.message_type
    sid = ev.group_id if stype == "group" else ev.user_id
    ayaka_event = AyakaEvent(
        session=AyakaSession(type=stype, id=sid),
        msg=msg,
        sender_id=ev.sender["user_id"],
        sender_name=ev.sender.get("card") or ev.sender["nickname"],
    )
    await bridge.handle_event(ayaka_event)


@singleton
def get_current_bot():
    return NoneBot()


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
    bot_id = next(bot.get_self_ids())
    for i in range(div_cnt):
        msgs = [
            {"user_id": bot_id, "nickname": "Ayaka Bot", "content": m}
            for m in msgs[i*div_len: (i+1)*div_len]
        ]
        await bot.call_action("send_group_forward_msg", group_id=int(id), messages=msgs)


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
    if bridge.ready:
        return

    bot = get_current_bot()
    prefix = list(bot.config.COMMAND_START)[0]
    separate = list(bot.config.COMMAND_SEP)[0]

    def get_prefix():
        return prefix

    def get_separate():
        return separate

    # 注册外部服务
    bridge.regist(send)
    bridge.regist(send_many)
    bridge.regist(get_prefix)
    bridge.regist(get_separate)
    bridge.regist(get_member_info)
    bridge.regist(get_member_list)
    bridge.regist(bot.on_startup)

    # 内部服务注册到外部
    bot.on("message")(handle_msg)

    # 其他初始化
    bot.on_startup(start_loop)

    bridge.ready = True
