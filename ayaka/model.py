'''提供基本模型'''
from typing import Optional
from pydantic import BaseModel


class AyakaSession(BaseModel):
    type: str
    id: str

    @property
    def mark(self):
        return f"{self.type} {self.id}"

    def __hash__(self):
        return hash(self.mark)


class AyakaSender(BaseModel):
    id: str
    name: str


class AyakaEvent(BaseModel):
    '''外部只要实例化AyakaEvent对象，就可以使用bridge.handle_event(event)来传递消息事件给AyakaCat'''
    session: AyakaSession
    sender: AyakaSender
    message: str
    origin: Optional["AyakaEvent"]


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
