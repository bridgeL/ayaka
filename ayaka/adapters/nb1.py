'''适配 hoshino机器人'''
from html import unescape
from math import ceil
from loguru import logger
import nonebot
from aiocqhttp import Event as CQEvent
from aiocqhttp.exceptions import ActionFailed
from ..bridge import bridge, GroupMemberInfo
from ..event import AyakaEvent
from ..helpers import singleton


async def handle_msg(ev: CQEvent):
    separate = " "

    # 处理消息，保留text、at、reply
    ms = ev.message
    at = None
    reply = None
    if ms[0].type == "reply":
        bot = get_current_bot()
        try:
            d = await bot.get_msg(message_id=ms[0].data["id"])
            reply = unescape(d["message"])
        except:
            pass
        else:
            at = ms[1].data["qq"]
            ms = ms[2:]

    args: list[str] = []
    for m in ms:
        if m.type == "text":
            arg = unescape(str(m))
            # 删除第一个空格，真无语
            if arg.startswith(" "):
                arg = arg[1:]
            if arg:
                args.append(arg)
        elif not at and m.type == "at":
            at = str(m.data["qq"])
        else:
            args.append(str(m))

    msg = separate.join(args)

    # 组成ayaka事件
    stype = ev.message_type
    sid = ev.group_id if stype == "group" else ev.user_id
    ayaka_event = AyakaEvent(
        session_type=stype,
        session_id=sid,
        sender_id=ev.sender["user_id"],
        sender_name=ev.sender.get("card") or ev.sender["nickname"],
        message=msg,
        at=at,
        reply=reply,
    )

    try:
        await bridge.handle_event(ayaka_event)
    except:
        logger.exception(f"ayaka 处理事件（{ayaka_event}）时发生错误")


@singleton
def get_current_bot():
    return nonebot.get_bot()


async def send_group(id: str, msg: str) -> bool:
    bot = get_current_bot()
    try:
        await bot.send_group_msg(group_id=int(id), message=msg)
    except ActionFailed:
        await bot.send_group_msg(group_id=int(id), message="群聊消息发送失败")
    else:
        return True


async def send_private(id: str, msg: str) -> bool:
    bot = get_current_bot()
    try:
        await bot.send_private_msg(user_id=int(id), message=msg)
    except ActionFailed:
        await bot.send_private_msg(user_id=int(id), message="私聊消息发送失败")
    else:
        return True


async def send_group_many(id: str, msgs: list[str]) -> bool:
    bot = get_current_bot()
    # 分割长消息组（不可超过100条
    div_len = 100
    div_cnt = ceil(len(msgs) / div_len)
    bot_id = next(bot.get_self_ids())
    try:
        for i in range(div_cnt):
            msgs = [
                {"user_id": bot_id, "nickname": "Ayaka Bot", "content": m}
                for m in msgs[i*div_len: (i+1)*div_len]
            ]
            await bot.call_action("send_group_forward_msg", group_id=int(id), messages=msgs)
    except ActionFailed:
        await bot.send_group_msg(group_id=int(id), message="合并转发消息发送失败")
    else:
        return True


async def get_member_info(gid: str, uid: str):
    bot = get_current_bot()
    try:
        user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
        return GroupMemberInfo(
            id=user["user_id"],
            name=user["card"] or user["nickname"],
            role=user["role"]
        )
    except:
        pass


async def get_member_list(gid: str):
    bot = get_current_bot()
    try:
        users = await bot.get_group_member_list(group_id=int(gid))
        return [
            GroupMemberInfo(
                id=user["user_id"],
                role="admin",
                name=user["card"] or user["nickname"],
            )
            for user in users
        ]
    except:
        pass

bot = get_current_bot()
prefixes = list(bot.config.COMMAND_START) or [""]


def get_prefixes():
    return prefixes


# 注册外部服务
bridge.regist(send_group)
bridge.regist(send_private)
bridge.regist(send_group_many)
bridge.regist(get_prefixes)
bridge.regist(get_member_info)
bridge.regist(get_member_list)
bridge.regist(bot.on_startup)

# 内部服务注册到外部
bot.on("message")(handle_msg)
