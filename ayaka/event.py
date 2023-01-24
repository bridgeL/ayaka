'''ayaka消息事件'''
from typing import Optional
from pydantic import BaseModel


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

    private_forward_id: Optional[str]
    '''私聊转发'''
