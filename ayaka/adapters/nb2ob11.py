'''适配 nonebot2机器人 onebot v11适配器'''
from html import unescape
from math import ceil
from loguru import logger
import nonebot
from nonebot.matcher import current_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment
from nonebot.exception import ActionFailed
from ..event import AyakaEvent
from ..bridge import bridge, GroupMemberInfo


async def handle_msg(bot: Bot, event: MessageEvent):
    separate = " "

    # 处理消息事件，保留text，reply，to_me或第一个at
    at = None
    reply = None
    if event.reply:
        reply = str(event.reply.message)
        at = str(event.reply.sender.user_id)
    if not at and event.to_me:
        at = bot.self_id

    args: list[str] = []
    for m in event.message:
        if m.type == "text":
            args.append(unescape(str(m)))
        elif not at and m.type == "at":
            at = str(m.data["qq"])
        else:
            args.append(str(m))

    msg = separate.join(args)

    # 组成ayaka事件
    stype = event.message_type
    sid = event.group_id if stype == "group" else event.user_id
    ayaka_event = AyakaEvent(
        session_type=stype,
        session_id=sid,
        sender_id=event.sender.user_id,
        sender_name=event.sender.card or event.sender.nickname,
        message=msg,
        at=at,
        reply=reply,
    )

    try:
        await bridge.handle_event(ayaka_event)
    except:
        logger.exception(f"ayaka 处理事件（{ayaka_event}）时发生错误")


def get_current_bot() -> Bot:
    return current_bot.get()


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
    try:
        for i in range(div_cnt):
            msgs = [
                MessageSegment.node_custom(
                    user_id=bot.self_id,
                    nickname="Ayaka Bot",
                    content=m
                )
                for m in msgs[i*div_len: (i+1)*div_len]
            ]
            await bot.send_group_forward_msg(group_id=int(id), messages=msgs)
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

driver = nonebot.get_driver()
prefixes = list(driver.config.command_start) or [""]


def get_prefixes():
    return prefixes


# 注册外部服务
bridge.regist(send_group)
bridge.regist(send_private)
bridge.regist(send_group_many)
bridge.regist(get_prefixes)
bridge.regist(get_member_info)
bridge.regist(get_member_list)
bridge.regist(driver.on_startup)

# 内部服务注册到外部
nonebot.on_message(handlers=[handle_msg], block=False, priority=5)
