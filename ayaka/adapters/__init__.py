import sys
from ..logger import ayaka_clog


def is_hoshino():
    if "hoshino" in sys.modules:
        ayaka_clog("识别到 <y>hoshino</y>，加载为hoshino插件")
        return True


def is_nb1():
    if "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            ayaka_clog("识别到 <y>nonebot1</y>，加载为nonebot1插件")
            return True


def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        ayaka_clog("识别到 <y>nonebot2 onebot11</y>，加载为nonebot2插件")
        return True


# hoshino
if is_hoshino():
    from . import hoshino as __hoshino

# nonebot1
elif is_nb1():
    from . import nb1 as __nb1

# nonebot2 onebot11
elif is_nb2ob11():
    from . import nb2ob11 as __nb2ob11

# console
else:
    ayaka_clog("未检测到环境信息，加载为<y>console</y>程序")
    from .console import run
