'''适配 hoshino 机器人'''
from hoshino import Service
from ayaka_utils import singleton
from .nb1 import Nonebot1Adapter
from ..adapter import regist


@singleton
class HoshinoAdapter(Nonebot1Adapter):
    '''hoshino 适配器'''

    @classmethod
    def get_current_bot(cls):
        '''获取当前bot'''
        return bot


bot = Service('ayaka').bot

HoshinoAdapter.name = "hoshino"


regist(HoshinoAdapter)
