'''提供基本模型'''
from typing import Optional
from pydantic import BaseModel


class AyakaChannel(BaseModel):
    '''会话'''
    type: str
    id: str

    @property
    def mark(self):
        return f"{self.type} {self.id}"

    def __hash__(self):
        return hash(self.mark)


class AyakaSender(BaseModel):
    '''消息发送者'''
    id: str
    name: str


class AyakaEvent(BaseModel):
    '''ayaka消息事件'''
    channel: AyakaChannel
    sender: AyakaSender
    message: str
    reply: Optional[str]
    at: Optional[str]
    origin_channel: Optional[AyakaChannel]


class User(BaseModel):
    id: str
    name: str
    role: str


class ResItem(BaseModel):
    '''资源项'''
    path: str
    '''下载地址的相对地址尾'''
    hash: str = ""
    '''资源的哈希值'''


class ResInfo(BaseModel):
    '''资源信息'''
    base: str
    '''下载地址的绝对地址头'''
    items: list[ResItem] = []
    '''资源项'''
