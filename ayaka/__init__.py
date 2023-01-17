'''
    ayaka - cat Cat CAT - 0.0.0.5b5
'''
# logger
from . import logger as __logger

# 有用的类
from .cat import AyakaCat, AyakaEvent
from .config import AyakaConfig
from .orm import AyakaDB, AyakaUserDB, AyakaGroupDB
from .helpers import load_data_from_file, debug_print, simple_repr
from .download import resource_download, resource_download_by_res_info, get_file_hash
from .model import ResInfo, ResItem, User, AyakaSession, AyakaEvent
from .bridge import bridge

# 根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，加载对应的代码
from . import adapters as __adapters

# 猫猫管理器
from . import master as __master
