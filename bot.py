from nonebot import init, get_app, get_driver, run, load_plugin
from nonebot.adapters.onebot.v11 import Adapter

init()
app = get_app()
driver = get_driver()
driver.register_adapter(Adapter)

# 加载插件
load_plugin("ayaka_games")

# # 临时 [-]
# load_plugin("ayaka_test")
# load_plugin("ayaka_test_extension")

if __name__ == "__main__":
    run(app="__mp_main__:app")
