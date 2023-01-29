'''
Ayaka - 猫猫，猫猫！ 

专注群聊、多人互动的插件开发

文档：https://bridgel.github.io/ayaka/

注意：文档版本与pypi包正式版本一致，因此其内容可能会落后于各个beta版
'''

# 确保logger第一个导入
from . import logger as __logger
# 根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，加载对应的代码
from .adapters import get_adapter, AyakaEvent
# 猫猫管理器
from . import master as __master

# 有用的类和方法
from .helpers import load_data_from_file, debug_print, simple_repr, ensure_dir_exists
from .download import resource_download, resource_download_by_res_info, get_file_hash, ResInfo, ResItem
from .database import get_session
from .config import AyakaConfig
from .core import AyakaCat
