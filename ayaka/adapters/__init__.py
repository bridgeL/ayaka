'''适配器，自动识别机器人框架和协议'''
import sys
from .adapter import AyakaAdapter, regist, get_adapter, adapter_dict
from .model import AyakaEvent, GroupMemberInfo
from ..logger import ayaka_clog
from ..config import root_config


def is_hoshino():
    if "hoshino" in sys.modules:
        ayaka_clog("识别到 <y>hoshino</y>，加载为hoshino插件")
        return True


def is_nb1():
    # 防止hoshino重复注册
    if "hoshino" not in sys.modules and "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            ayaka_clog("识别到 <y>nonebot1</y>，加载为nonebot1插件")
            return True


def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        ayaka_clog("识别到 <y>nonebot2 onebot11</y>，加载为nonebot2插件")
        return True


# 自动导入
if root_config.auto_detect:
    # hoshino
    if is_hoshino():
        from .hoshino import HoshinoAdapter
        regist(HoshinoAdapter)

    # nonebot1
    if is_nb1():
        from .nb1 import Nonebot1Adapter
        regist(Nonebot1Adapter)

    # nonebot2 onebot11
    if is_nb2ob11():
        from .nb2.ob11 import Nonebot2Onebot11Adapter
        regist(Nonebot2Onebot11Adapter)

        if root_config.auto_ob11_qqguild_patch:
            from .nb2.qqguild_patch import Nonebot2Onebot11QQguildPatchAdapter
            regist(Nonebot2Onebot11QQguildPatchAdapter)

    if not adapter_dict:
        ayaka_clog("未检测到环境信息，加载为<y>console</y>程序")
        from .console import ConsoleAdapter, run
        regist(ConsoleAdapter)
