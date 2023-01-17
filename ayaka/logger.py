import sys
from loguru import logger
from functools import partial
from .helpers import ensure_dir_exists

logger.level("AYAKA", no=27, icon="⚡", color="<blue>")

ayaka_clog = partial(logger.opt(colors=True).log, "AYAKA")
'''彩色 ayaka log方法（有<>不匹配风险）'''
ayaka_log = partial(logger.log, "AYAKA")
'''单色 ayaka log方法'''
clogger = logger.opt(colors=True)
'''彩色 logger（有<>不匹配风险）'''

logger_format = "<g>{time:MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>] <c><u>{name}</u></c> | {message}"


# 仅移除原生logger
try:
    logger.remove(0)
except ValueError:
    pass

# 若无logger，则需新建（避免与nonebot同时建立两种格式的handler）
# 注意：该特性并无正式用法，loguru维护者不保证其在未来可用
# https://github.com/Delgan/loguru/issues/201
if not logger._core.handlers:
    # 输出至终端
    logger.add(sys.stdout, diagnose=False, format=logger_format)

# 输出报错至本地日志文件
error_path = ensure_dir_exists("data/ayaka/error.log")
file = error_path.open("a+", encoding="utf8")
logger.add(file, level="ERROR", diagnose=False, format=logger_format)
