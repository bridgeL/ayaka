'''管理插件配置，提供读写支持'''
import json
import inflection
from loguru import logger
from typing import Optional
from pydantic import ValidationError, BaseModel, validator
from ayaka_utils import ensure_dir_exists

AYAKA_VERSION = "0.0.4.5"


class AyakaConfig(BaseModel):
    '''配置'''

    __config_dir__ = None
    '''配置文件的目录名，可自定义，默认为ayaka'''
    __config_name__ = None
    '''配置文件的名称，可自定义，默认为类名的下划线模式'''
    __config_path__ = None
    '''配置文件的地址，最好不要自定义它'''

    @classmethod
    @property
    def config_name(cls):
        if not cls.__config_name__:
            cls.__config_name__ = inflection.underscore(cls.__name__)
        return cls.__config_name__

    @classmethod
    @property
    def config_dir(cls):
        if not cls.__config_dir__:
            cls.__config_dir__ = "ayaka"
        return cls.__config_dir__

    @classmethod
    @property
    def config_path(cls):
        if not cls.__config_path__:
            cls.__config_path__ = ensure_dir_exists(
                f"data/{cls.config_dir}/{cls.config_name}.json")
        return cls.__config_path__

    def __init__(self, **data):
        path = self.config_path
        try:
            # 存在则读取
            if path.exists():
                with path.open("r", encoding="utf8") as f:
                    data = json.load(f)

            # 载入数据
            super().__init__(**data)

        except ValidationError as e:
            logger.error(
                f"导入配置失败，请检查{path}的配置是否正确；如果不确定出错的原因，可以尝试更新插件，删除旧配置并重启bot")
            raise e

        # 强制更新（更新默认值）
        self.save()
        logger.opt(colors=True).debug(f"已载入配置文件 <g>{path}</g>")

    def __setattr__(self, name, value):
        if getattr(self, name) != value:
            super().__setattr__(name, value)
            self.save()

    def save(self):
        '''修改可变成员变量后，需要使用该方法才能保存其值到文件'''
        data = self.dict()
        path = self.config_path
        with path.open("w+", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=0, indent=4)


class RootConfig(AyakaConfig):
    '''根配置'''

    version: str = AYAKA_VERSION
    '''版本号'''

    auto_ob11_qqguild_patch: bool = True
    '''在ob11协议中自动使用qqguild_patch'''

    prefixes: list[str] = ["", "#"]
    separate: str = " "

    ws_reverse: Optional[str]

    @validator('prefixes')
    def prefixes_must_be_not_empty(cls, v):
        if not v:
            raise ValueError('prefixes must be not empty')
        return v


logger.opt(colors=True).info(f"<y>ayaka</y> 当前版本 <y>{AYAKA_VERSION}</y>")
root_config = RootConfig()


def get_root_config():
    '''获取ayaka根配置'''
    return root_config
