'''管理插件配置，提供读写支持'''
import json
from loguru import logger
from pydantic import ValidationError, BaseModel
from .helpers import ensure_dir_exists, singleton

AYAKA_VERSION = "0.0.3.2"


@singleton
def get_data_path():
    return ensure_dir_exists("data/ayaka")


class AyakaConfig(BaseModel):
    '''继承时请填写`__config_name__`

    该配置保存在data/ayaka/<__config_name__>.json

    在修改不可变成员属性时，`AyakaConfig`会自动写入到本地文件，但修改可变成员属性时，需要手动执行save函数
    '''
    __config_name__ = ""
    '''配置文件的名称'''

    def __init__(self, **data):
        name = self.__config_name__
        if not name:
            raise Exception("__config_name__不可为空")

        try:
            path = get_data_path() / f"{name}.json"
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
        logger.opt(colors=True).debug(f"已载入配置文件 <g>{name}</g>")

    def __setattr__(self, name, value):
        if getattr(self, name) != value:
            super().__setattr__(name, value)
            self.save()

    def save(self):
        '''修改可变成员变量后，需要使用该方法才能保存其值到文件'''
        name = self.__config_name__
        data = self.dict()
        path = get_data_path() / f"{name}.json"
        with path.open("w+", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=0, indent=4)


@singleton
class RootConfig(AyakaConfig):
    '''根配置'''

    __config_name__ = "root"

    version: str = AYAKA_VERSION
    '''版本号'''

    auto_ob11_qqguild_patch: bool = True
    '''在ob11协议中自动使用qqguild_patch'''

    block_cat_dict: dict[str, list[str]] = {}
    '''屏蔽列表，dict[cat_name:list[session_mark]]'''


def get_root_config():
    '''获取ayaka根配置'''
    return RootConfig()
