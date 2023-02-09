'''适配 nonebot1 机器人'''
from math import ceil
from html import unescape
from typing import Awaitable, Callable

import nonebot
from aiocqhttp import Event as CQEvent
from aiocqhttp.exceptions import ActionFailed

from ..adapter import AyakaAdapter
from ..model import GroupMemberInfo, AyakaEvent


class Nonebot1Adapter(AyakaAdapter):
    '''nonebot1 适配器'''

    def __init__(self) -> None:
        bot.on("message")(self.handle)

    async def send_group(self, id: str, msg: str) -> bool:
        '''发送消息到指定群聊'''
        try:
            await bot.send_group_msg(group_id=int(id), message=msg)
        except ActionFailed:
            await bot.send_group_msg(group_id=int(id), message="群聊消息发送失败")
        else:
            return True

    async def send_private(self, id: str, msg: str) -> bool:
        '''发送消息到指定私聊'''
        try:
            await bot.send_private_msg(user_id=int(id), message=msg)
        except ActionFailed:
            await bot.send_private_msg(user_id=int(id), message="私聊消息发送失败")
        else:
            return True

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
        '''发送消息组到指定群聊'''
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

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
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

    async def handle(self, ev: CQEvent):
        '''将输入的参数加工为ayaka_event，请在最后调用self.handle_event进行处理'''

        # 处理消息，保留text、at、reply
        ms = ev.message
        raw_msg = ms
        
        at = None
        reply = None
        if ms[0].type == "reply":
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

        msg = self.separate.join(args)

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
            raw_message=raw_msg
        )

        # 处理事件
        await self.handle_event(ayaka_event)

    def _on_startup(self, async_func: Callable[..., Awaitable]):
        '''asgi服务启动后钩子，注册回调必须是异步函数'''
        bot.on_startup(async_func)

    @classmethod
    def get_current_bot(cls):
        '''获取当前bot'''
        return bot


bot = nonebot.get_bot()

Nonebot1Adapter.name = "nb1"
Nonebot1Adapter.prefixes = list(bot.config.COMMAND_START) or [""]
