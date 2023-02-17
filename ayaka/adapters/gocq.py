'''直接连接gocq'''
import re
import sys
import json
import asyncio
import dataclasses
from math import ceil
from loguru import logger
from html import unescape
from typing import Any, Optional
from fastapi import FastAPI, WebSocket

from .adapter import GroupMemberInfo, AyakaEvent, AyakaAdapter, get_first_adapter, regist
from ..config import get_root_config


class DataclassEncoder(json.JSONEncoder):
    """在JSON序列化 `Message` (List[Dataclass]) 时使用的 `JSONEncoder`"""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class ResultStore:
    _seq = 1
    _futures: dict[int, asyncio.Future] = {}

    @classmethod
    def get_seq(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s

    @classmethod
    def add_result(cls, result: dict[str, Any]):
        echo = result.get("echo")
        if not isinstance(echo, dict):
            return

        seq = echo.get("seq")
        if not isinstance(seq, int):
            return

        future = cls._futures.get(seq)
        if not future:
            return

        future.set_result(result)

    @classmethod
    async def fetch(
        cls, seq: int, timeout: Optional[float]
    ) -> dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        cls._futures[seq] = future
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            raise
        finally:
            del cls._futures[seq]


app = None
host = None
port = None


class GoCQAdapter(AyakaAdapter):
    '''直接连接gocq 适配器'''

    def __init__(self) -> None:
        ws_url = get_root_config().ws_reverse
        if not ws_url:
            raise Exception("没有设置ws反向连接地址(ws_reverse)")

        r = re.search(r"^ws://((\d+\.){3}\d+):(\d+)/(.+)", ws_url)
        if not r:
            raise Exception(
                "没有正确设置ws反向连接地址(ws_reverse)，格式：ws://{host}:{port}/{path}")

        global host, port
        host = r.group(1)
        port = int(r.group(3))
        path = r.group(4)

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

        app.websocket_route("/"+path)(self.start)

    async def start(self, ws: WebSocket):
        self.ws = ws
        self.bot_id = ws.headers.get("x-self-id")

        # 建立ws连接
        await ws.accept()
        logger.opt(colors=True).success(f"已连接到 <y>{self.bot_id}</y>")

        try:
            # 监听循环
            while True:
                data = await ws.receive()
                data = data["text"]
                json_data: dict = json.loads(data)

                if "echo" in json_data:
                    ResultStore.add_result(json_data)

                elif json_data.get("post_type") == "message":
                    asyncio.create_task(self.handle(json_data))

        except:
            logger.exception("连接中断")
        finally:
            # 结束ws连接
            await ws.close()

    async def send_group(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定群聊'''
        try:
            await self.call_api("send_group_msg", group_id=int(id), message=msg)
        except:
            await self.call_api("send_group_msg", group_id=int(id), message="群聊消息发送失败")
        else:
            return True

    async def send_private(self, id: str, msg: str, bot_id: str | None = None) -> bool:
        '''发送消息到指定私聊'''
        try:
            await self.call_api("send_private_msg", user_id=int(id), message=msg)
        except:
            await self.call_api("send_private_msg", user_id=int(id), message="私聊消息发送失败")
        else:
            return True

    async def send_group_many(self, id: str, msgs: list[str], bot_id: str | None = None) -> bool:
        '''发送消息组到指定群聊'''
        # 分割长消息组（不可超过100条
        div_len = 100
        div_cnt = ceil(len(msgs) / div_len)
        try:
            for i in range(div_cnt):
                msgs = [
                    {"user_id": self.bot_id, "nickname": "Ayaka Bot", "content": m}
                    for m in msgs[i*div_len: (i+1)*div_len]
                ]
                await self.call_api("send_group_forward_msg", group_id=int(id), messages=msgs)
        except:
            await self.call_api("send_group_msg", group_id=int(id), message="合并转发消息发送失败")
        else:
            return True

    async def get_group_member(self, gid: str, uid: str) -> GroupMemberInfo | None:
        '''获取群内某用户的信息'''
        try:
            user = await self.call_api("get_group_member_info", group_id=int(gid), user_id=int(uid))
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
            users = await self.call_api("get_group_member_list", group_id=int(gid))
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

    async def call_api(self, api: str, **kwargs):
        # 生成 seq码 和 待发送的json数据
        seq = ResultStore.get_seq()
        json_data = json.dumps(
            {"action": api, "params": kwargs, "echo": {"seq": seq}},
            cls=DataclassEncoder,
        )

        try:
            await self.ws.send_text(json_data)
            # 默认30s超时
            result = await ResultStore.fetch(seq, 30)
            if isinstance(result, dict):
                if result.get("status") == "failed":
                    raise
                return result.get("data")

        except:
            logger.exception("发送消息失败")

    async def handle(self, data: dict):
        '''将输入的参数加工为ayaka_event，请在最后调用self.handle_event进行处理'''

        # 处理消息事件，保留text，reply，to_me或第一个at
        at = None
        reply = None
        msg = data["message"]
        r = re.search(r"\[CQ:reply,id=(-?\d+)\]", msg)
        if r:
            mid = r.group(1)
            msg = re.sub(r"\[CQ:reply,id=(-?\d+)\]", "", msg)
            try:
                d = await self.call_api("get_msg", message_id=mid)
                reply = unescape(d["message"])
            except:
                pass

        r = re.search(r"\[CQ:at,qq=(\d+)\]", msg)
        if r:
            at = r.group(1)
            msg = re.sub(r"\[CQ:at,qq=(\d+)\]", "", msg)

        # # 组成ayaka事件
        stype = data["message_type"]
        sid = data["group_id"] if stype == "group" else data["user_id"]
        ayaka_event = AyakaEvent(
            session_type=stype,
            session_id=sid,
            sender_id=data["sender"]["user_id"],
            sender_name=data["sender"].get(
                "card") or data["sender"]["nickname"],
            message=msg,
            at=at,
            reply=reply,
            raw_message=data["message"]
        )

        # 处理事件
        await self.handle_event(ayaka_event)


GoCQAdapter.name = "gocq"
regist(GoCQAdapter)


def run(**kwargs):
    '''运行'''
    import uvicorn
    kwargs.setdefault("app", f"{__name__}:app")
    kwargs.setdefault("host", host)
    kwargs.setdefault("port", port)
    kwargs.setdefault("reload", True)
    uvicorn.run(**kwargs)
