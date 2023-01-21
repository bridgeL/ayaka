'''
    管理插件配置，提供读写支持
'''
import json
from pydantic import ValidationError, BaseModel
from .logger import logger, clogger, logger_format
from .model import AyakaChannel
from .helpers import ensure_dir_exists

AYAKA_VERSION = "0.0.1.4b1"
clogger.success(f"<y>ayaka</y> 当前版本 <y>{AYAKA_VERSION}</y>")
data_path = ensure_dir_exists("data/ayaka")


class AyakaConfig(BaseModel):
    '''继承时请填写`__config_name__`

    该配置保存在data/ayaka/<__config_name__>.json

    在修改不可变成员属性时，`AyakaConfig`会自动写入到本地文件，但修改可变成员属性时，需要手动执行save函数
    '''
    __config_name__ = ""
    '''配置文件的名称'''

    def __init__(self):
        name = self.__config_name__
        if not name:
            raise Exception("__config_name__不可为空")

        # 默认空数据
        data = {}

        try:
            path = data_path / f"{name}.json"
            # 存在则读取
            if path.exists():
                with path.open("r", encoding="utf8") as f:
                    data = json.load(f)

            # 载入数据
            super().__init__(**data)

        except ValidationError as e:
            logger.error(
                f"导入配置失败，请检查{name}的配置是否正确；如果不确定出错的原因，可以尝试更新插件，删除旧配置并重启bot")
            raise e

        # 强制更新（更新默认值）
        self.save()
        clogger.debug(f"已载入配置文件 <g>{name}</g>")

    def __setattr__(self, name, value):
        if getattr(self, name) != value:
            super().__setattr__(name, value)
            self.save()

    def save(self):
        '''修改可变成员变量后，需要使用该方法才能保存其值到文件'''
        name = self.__config_name__
        data = self.dict()
        path = data_path / f"{name}.json"
        with path.open("w+", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=0, indent=4)


class RootConfig(AyakaConfig):
    '''根配置'''

    __config_name__ = "root"

    version: str = AYAKA_VERSION
    '''版本号'''

    block_cat_dict: dict[str, list[AyakaChannel]] = {}
    '''屏蔽列表'''

    error_report: bool = False
    '''记录所有错误'''


root_config = RootConfig()
'''ayaka根配置'''

root_config.version = AYAKA_VERSION


# 输出报错至本地日志文件
if root_config.error_report:
    error_path = ensure_dir_exists("data/ayaka/error.log")
    file = error_path.open("a+", encoding="utf8")
    logger.add(file, level="ERROR", diagnose=False, format=logger_format)
