'''适配 nonebot2 机器人 onebot v11 协议 兼容 qqguild'''
from html import unescape
from typing import Literal
from pydantic import Field, validator, root_validator, parse_obj_as

import nonebot
from nonebot.utils import escape_tag
from nonebot.typing import overrides
from nonebot.adapters.onebot.v11 import Adapter, Message, MessageEvent, MessageSegment, Bot, Event
from nonebot.exception import ActionFailed

from .ob11 import Nonebot2Onebot11Adapter
from ..model import GroupMemberInfo, AyakaEvent


class GuildMessageEvent(MessageEvent):
    """频道消息"""

    message_type: Literal["guild"]
    self_tiny_id: int
    message_id: str
    guild_id: int
    channel_id: int

    raw_message: str = Field(alias="message")
    font: None = None

    @validator("raw_message", pre=True)
    def _validate_raw_message(cls, raw_message):
        if isinstance(raw_message, str):
            return raw_message
        elif isinstance(raw_message, list):
            return str(parse_obj_as(Message, raw_message))
        raise ValueError("unknown raw message type")

    @root_validator(pre=False)
    def _validate_is_tome(cls, values):
        message = values.get("message")
        self_tiny_id = values.get("self_tiny_id")
        message, is_tome = cls._check_at_me(
            message=message, self_tiny_id=self_tiny_id)
        values.update(
            {"message": message, "to_me": is_tome, "raw_message": str(message)}
        )
        return values

    @overrides(Event)
    def is_tome(self) -> bool:
        return self.to_me or any(
            str(msg_seg.data.get("qq", "")) == str(self.self_tiny_id)
            for msg_seg in self.message
            if msg_seg.type == "at"
        )

    @overrides(Event)
    def get_event_description(self) -> str:
        return (
            f"Message {self.message_id} from "
            f'{self.user_id}@[Guild:{self.guild_id}/Channel:{self.channel_id}] "%s"'
            % "".join(
                map(
                    lambda x: escape_tag(str(x))
                    if x.is_text()
                    else f"<le>{escape_tag(str(x))}</le>",
                    self.message,
                )
            )
        )

    @overrides(MessageEvent)
    def get_session_id(self) -> str:
        return f"guild_{self.guild_id}_channel_{self.channel_id}_{self.user_id}"

    @staticmethod
    def _check_at_me(message: Message, self_tiny_id: int) -> tuple[Message, bool]:
        """检查消息开头或结尾是否存在 @机器人，去除并赋值 event.to_me"""
        is_tome = False
        # ensure message not empty
        if not message:
            message.append(MessageSegment.text(""))

        def _is_at_me_seg(segment: MessageSegment):
            return segment.type == "at" and str(segment.data.get("qq", "")) == str(
                self_tiny_id
            )

        # check the first segment
        if _is_at_me_seg(message[0]):
            is_tome = True
            message.pop(0)
            if message and message[0].type == "text":
                message[0].data["text"] = message[0].data["text"].lstrip()
                if not message[0].data["text"]:
                    del message[0]
            if message and _is_at_me_seg(message[0]):
                message.pop(0)
                if message and message[0].type == "text":
                    message[0].data["text"] = message[0].data["text"].lstrip()
                    if not message[0].data["text"]:
                        del message[0]

        if not is_tome:
            # check the last segment
            i = -1
            last_msg_seg = message[i]
            if (
                last_msg_seg.type == "text"
                and not last_msg_seg.data["text"].strip()
                and len(message) >= 2
            ):
                i -= 1
                last_msg_seg = message[i]

            if _is_at_me_seg(last_msg_seg):
                is_tome = True
                del message[i:]

        if not message:
            message.append(MessageSegment.text(""))

        return message, is_tome


class Nonebot2Onebot11QQguildPatchAdapter(Nonebot2Onebot11Adapter):
    '''nonebot2 onebot v11 qqguild patch 适配器'''

    def first_init(self) -> None:
        '''在第一次初始化时执行'''
        Adapter.add_custom_model(GuildMessageEvent)
        nonebot.on_message(handlers=[self.handle], block=False, priority=5)

    async def send_group(self, id: str, msg: str) -> bool:
        '''发送消息到指定群聊'''
        bot = self.get_current_bot()

        guild_id, channel_id = id.split(" ")

        try:
            await bot.send_guild_channel_msg(
                guild_id=guild_id,
                channel_id=channel_id,
                message=msg,
            )
        except ActionFailed:
            await bot.send_guild_channel_msg(
                guild_id=guild_id,
                channel_id=channel_id,
                message="群聊消息发送失败",
            )
        else:
            return True

    async def send_private(self, id: str, msg: str) -> bool:
        '''发送消息到指定私聊'''

        # ---- 待完成 ----
        await super().send_private(id, msg)

    async def send_group_many(self, id: str, msgs: list[str]) -> bool:
        '''发送消息组到指定群聊'''
        for msg in msgs:
            await self.send_group(id, msg)

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
        bot = self.get_current_bot()
        guild_id, channel_id = gid.split(" ")
        data = await bot.get_guild_member_profile(guild_id=guild_id, user_id=uid)
        return GroupMemberInfo(id=uid, name=data["nickname"], role=str(data["roles"]))

    async def get_group_members(self, gid: str) -> list[GroupMemberInfo]:
        '''获取群内所有用户的信息'''
        # ---- 待完善 ----
        bot = self.get_current_bot()
        guild_id, channel_id = gid.split(" ")

        # 第一页
        data = await bot.get_guild_member_list(guild_id=guild_id)

        return [
            GroupMemberInfo(
                id=m["tiny_id"],
                name=m["nickname"],
                role=m["role_name"]
            )
            for m in data["members"]
        ]

    async def handle(self, bot: Bot, event: GuildMessageEvent):
        '''将输入的参数加工为ayaka_event，请在最后调用self.handle_event进行处理'''

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
        stype = "group"
        sid = f"{event.guild_id} {event.channel_id}"
        ayaka_event = AyakaEvent(
            session_type=stype,
            session_id=sid,
            sender_id=event.sender.user_id,
            sender_name=event.sender.card or event.sender.nickname,
            message=msg,
            at=at,
            reply=reply,
        )

        # 处理事件
        await self.handle_event(ayaka_event)


Nonebot2Onebot11QQguildPatchAdapter.name = "nb2.ob11.qqguild_patch"
