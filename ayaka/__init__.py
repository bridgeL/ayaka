'''
Ayaka - 猫猫，猫猫！ 

专注群聊、多人互动的插件开发

文档：https://bridgel.github.io/ayaka/

注意：文档版本与pypi包正式版本一致，因此其内容可能会落后于各个beta版
'''
from . import logger as __logger
from . import master as __master

from .adapters import get_adapter, AyakaEvent
from .config import AyakaConfig, AYAKA_VERSION
from .cat import AyakaCat
from .subscribe import AyakaSubscribe
from .database import AyakaDB, get_db
from .download import resource_download, resource_download_by_res_info, get_file_hash, ResInfo, ResItem

from ayaka_utils import load_data_from_file, debug_print, simple_repr, ensure_dir_exists
