import sys
from loguru import logger
from functools import partial

logger.level("AYAKA", no=27, icon="⚡", color="<blue>")

ayaka_clog = partial(logger.opt(colors=True).log, "AYAKA")
'''彩色 ayaka log方法（有<>不匹配风险）'''
ayaka_log = partial(logger.log, "AYAKA")
'''单色 ayaka log方法'''
clogger = logger.opt(colors=True)
'''彩色 logger（有<>不匹配风险）'''


# 移除原生logger
try:
    logger.remove(0)
except ValueError:
    pass

# 若再无logger，则需新建
if not logger._core.handlers:
    logger.add(
        sys.stdout,
        diagnose=False,
        format="<g>{time:MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>] <c><u>{name}</u></c> | {message}",
    )
