'''猜测机器人框架'''
import sys
from ..logger import ayaka_clog
from ..helpers import singleton


@singleton
def is_hoshino():
    if "hoshino" in sys.modules:
        ayaka_clog("识别到 <y>hoshino</y>")
        return True


@singleton
def is_nb1():
    # 防止hoshino重复注册
    if "hoshino" not in sys.modules and "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            ayaka_clog("识别到 <y>nonebot1</y>")
            return True


@singleton
def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        ayaka_clog("识别到 <y>nonebot2 onebot11</y>")
        return True


@singleton
def is_no_env():
    if is_hoshino():
        return
    if is_nb1():
        return
    if is_nb2ob11():
        return

    ayaka_clog("未检测到环境信息，加载为<y>console</y>程序")
    return True
