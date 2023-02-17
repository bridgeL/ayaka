'''适配 nonebot2 机器人 onebot v11 协议'''
from math import ceil
from html import unescape
from typing import Awaitable, Callable

import nonebot
from nonebot.matcher import current_bot
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment
from nonebot.exception import ActionFailed

from ..adapter import GroupMemberInfo, AyakaEvent, AyakaAdapter, regist
from ...config import get_root_config


driver = nonebot.get_driver()


class Nonebot2Onebot11Adapter(AyakaAdapter):
    '''nonebot2 onebot v11 适配器'''

    def __init__(self) -> None:
        self.asgi = nonebot.get_app()
        nonebot.on_message(handlers=[self.handle], block=False, priority=5)

    async def send_group(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定群聊'''
        if bot_id:
            bot = nonebot.get_bot(bot_id)
        else:
            bot = self.get_current_bot()

        try:
            await bot.send_group_msg(group_id=int(id), message=msg)
        except ActionFailed:
            await bot.send_group_msg(group_id=int(id), message="群聊消息发送失败")
        else:
            return True

    async def send_private(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定私聊'''
        if bot_id:
            bot = nonebot.get_bot(bot_id)
        else:
            bot = self.get_current_bot()

        try:
            await bot.send_private_msg(user_id=int(id), message=msg)
        except ActionFailed:
            await bot.send_private_msg(user_id=int(id), message="私聊消息发送失败")
        else:
            return True

    async def send_group_many(self, id: str, msgs: list[str], bot_id: str | None = None) -> bool:
        '''发送消息组到指定群聊'''
        if bot_id:
            bot = nonebot.get_bot(bot_id)
        else:
            bot = self.get_current_bot()

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

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
        bot = self.get_current_bot()
        try:
            user = await bot.get_group_member_info(group_id=int(gid), user_id=int(uid))
            return GroupMemberInfo(
                id=user["user_id"],
                name=user["card"] or user["nickname"],
                role=user["role"]
            )
        except:
            pass

    async def get_group_members(self, gid: str) -> list[GroupMemberInfo]:
        '''获取群内所有用户的信息'''
        bot = self.get_current_bot()
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

    async def handle(self, bot: Bot, event: MessageEvent):
        '''将输入的参数加工为ayaka_event，请在最后调用self.handle_event进行处理'''

        # 排除频道适配事件
        if hasattr(event, "guild_id"):
            return

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

        msg = self.separate.join(args)

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
            raw_message=event.raw_message
        )

        # 处理事件
        await self.handle_event(ayaka_event)

    def _on_startup(self, async_func: Callable[..., Awaitable]):
        '''asgi服务启动后钩子，注册回调必须是异步函数'''
        driver.on_startup(async_func)

    def _on_shutdown(self, async_func: Callable[..., Awaitable]):
        '''asgi服务关闭后钩子，注册回调必须是异步函数'''
        driver.on_shutdown(async_func)

    @classmethod
    def get_current_bot(cls) -> Bot:
        '''获取当前bot'''
        try:
            return current_bot.get()
        except LookupError:
            return


Nonebot2Onebot11Adapter.name = "nb2.ob11"
regist(Nonebot2Onebot11Adapter)

if get_root_config().auto_ob11_qqguild_patch:
    from .qqguild_patch import Nonebot2Onebot11QQguildPatchAdapter
