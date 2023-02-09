# 异味代码...但是不想改
class InitCtrl:
    def __init__(self) -> None:
        self.done = False

    def init_all(self):
        '''初始化ayaka，仅执行一次'''
        if self.done:
            return
        self.done = True

        # 加载错误日志记录
        from .logger import init_error_log
        init_error_log()

        # 初始化根配置
        from .config import get_root_config
        get_root_config()

        # 加载适配器
        from .adapters import auto_load_adapter
        auto_load_adapter()

        # 初始化数据库
        from .database import db_dict
        for db in db_dict.values():
            db.init()

        # 加载猫猫管理器
        from . import master



init_ctrl = InitCtrl()
