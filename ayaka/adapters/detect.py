'''猜测机器人框架'''
import sys
from loguru import logger
from .adapter import regist
from ..helpers import singleton
from ..config import get_root_config


@singleton
def is_hoshino():
    if "hoshino" in sys.modules:
        logger.opt(colors=True).info("识别到 <y>hoshino</y>")
        return True


@singleton
def is_nb1():
    # 防止hoshino重复注册
    if "hoshino" not in sys.modules and "nonebot" in sys.modules:
        if hasattr(sys.modules["nonebot"], "NoneBot"):
            logger.opt(colors=True).info("识别到 <y>nonebot1</y>")
            return True


@singleton
def is_nb2ob11():
    if "nonebot.adapters.onebot.v11" in sys.modules:
        logger.opt(colors=True).info("识别到 <y>nonebot2 onebot11</y>")
        return True


@singleton
def is_no_env():
    if is_hoshino():
        return
    if is_nb1():
        return
    if is_nb2ob11():
        return

    logger.opt(colors=True).info("未检测到环境信息，加载为<y>console</y>程序")
    return True


@singleton
def auto_load_adapter():
    '''自动加载适配器'''

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

        if get_root_config().auto_ob11_qqguild_patch:
            from .nb2.qqguild_patch import Nonebot2Onebot11QQguildPatchAdapter
            regist(Nonebot2Onebot11QQguildPatchAdapter)

    if is_no_env():
        from .console import ConsoleAdapter
        regist(ConsoleAdapter)
