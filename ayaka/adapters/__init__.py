'''适配器，自动识别机器人框架和协议'''
from .adapter import AyakaAdapter, regist, get_adapter
from .model import AyakaEvent, GroupMemberInfo
from .detect import auto_load_adapter
