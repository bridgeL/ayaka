import sys
from loguru import logger


def is_hoshino():
    if "hoshino" in sys.modules:
        logger.opt(colors=True).success("识别到 <y>hoshino</y>，加载为hoshino插件")
        return True


def is_nb1():
    if "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            logger.opt(colors=True).success("识别到 <y>nonebot1</y>，加载为nonebot1插件")
            return True


def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        logger.opt(colors=True).success("识别到 <y>nonebot2 onebot11</y>，加载为nonebot2插件")
        return True


# hoshino
if is_hoshino():
    from .hoshino import regist
    regist()

# nonebot1
elif is_nb1():
    from .nb1 import regist
    regist()

# nonebot2 onebot11
elif is_nb2ob11():
    from .nb2ob11 import regist
    regist()

# console
else:
    logger.opt(colors=True).success("<w>未检测到环境信息，加载为<y>console</y>程序</w>")
    from .console import run
