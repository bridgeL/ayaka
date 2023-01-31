'''适配 hoshino 机器人'''
from hoshino import Service, config
from .nb1 import Nonebot1Adapter


class HoshinoAdapter(Nonebot1Adapter):
    '''hoshino 适配器'''

    @classmethod
    def get_current_bot(cls):
        '''获取当前bot'''
        return bot


bot = Service('ayaka').bot

HoshinoAdapter.name = "hoshino"
HoshinoAdapter.prefixes = list(config.COMMAND_START) or [""]
