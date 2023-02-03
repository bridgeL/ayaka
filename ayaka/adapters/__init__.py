'''适配器，自动识别机器人框架和协议'''
from .adapter import AyakaAdapter, regist, get_adapter, init_all
from .model import AyakaEvent, GroupMemberInfo
