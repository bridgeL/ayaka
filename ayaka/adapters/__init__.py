'''适配器，自动识别机器人框架和协议'''
from .adapter import AyakaAdapter, regist, get_adapter
from .model import AyakaEvent, GroupMemberInfo
from .detect import is_no_env, is_hoshino, is_nb1, is_nb2ob11
from ..config import root_config

# 自动导入
if root_config.auto_detect:
    # hoshino
    if is_hoshino():
        from .nb1.hoshino import HoshinoAdapter
        regist(HoshinoAdapter)

    # nonebot1
    if is_nb1():
        from .nb1.nb1 import Nonebot1Adapter
        regist(Nonebot1Adapter)

    # nonebot2 onebot11
    if is_nb2ob11():
        from .nb2.ob11 import Nonebot2Onebot11Adapter
        regist(Nonebot2Onebot11Adapter)

        if root_config.auto_ob11_qqguild_patch:
            from .nb2.qqguild_patch import Nonebot2Onebot11QQguildPatchAdapter
            regist(Nonebot2Onebot11QQguildPatchAdapter)

    if is_no_env():
        from .console import ConsoleAdapter, run
        regist(ConsoleAdapter)
