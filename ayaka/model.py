'''提供基本模型'''
from typing import Optional
from pydantic import BaseModel


class AyakaChannel(BaseModel):
    '''频道'''
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
    '''消息来自哪个频道/群聊/私聊'''
    sender: AyakaSender
    '''消息发送者'''
    message: str
    '''当前消息'''
    reply: Optional[str]
    '''回复消息，如果gocq获取不到则为空字符串'''
    at: Optional[str]
    '''消息中的第一个at'''
    origin_channel: Optional[AyakaChannel]
    '''最初的频道（针对监听转发功能设置）'''


class GroupMember(BaseModel):
    id: str
    name: str
    role: Optional[str]
    '''群身份'''


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
