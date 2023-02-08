'''GroupMemberInfo和AyakaEvent'''
from typing import Optional
from pydantic import BaseModel


class GroupMemberInfo(BaseModel):
    id: str
    name: str
    role: Optional[str]
    '''群主、管理员、普通用户'''


class AyakaEvent(BaseModel):
    '''ayaka消息事件'''

    session_type: str
    '''消息会话类型'''
    session_id: str
    '''消息会话id'''
    sender_id: str
    '''消息发送者id'''
    sender_name: str
    '''消息发送者名称'''
    message: str
    '''当前消息'''
    reply: Optional[str]
    '''回复消息，如果gocq获取不到则为空字符串'''
    at: Optional[str]
    '''消息中的第一个at对象的uid'''
    raw_message: str
    '''从gocq收到的原始消息'''

    private_forward_id: Optional[str]
    '''私聊转发'''
