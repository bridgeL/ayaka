<div align="center">

# Ayaka - 猫猫，猫猫！ - 0.0.3.1

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ayaka)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ayaka)
![PyPI - License](https://img.shields.io/pypi/l/ayaka)
![PyPI](https://img.shields.io/pypi/v/ayaka)

专注群聊、多人互动的插件开发

</div>

根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，已支持

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebotv11](https://github.com/nonebot/adapter-onebot)适配器，借助[qqguild_patch](https://github.com/mnixry/nonebot-plugin-guild-patch)同时可适配qqguild)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其作为console程序离线运行

## 文档

https://bridgel.github.io/ayaka/

注意：文档版本与pypi包正式版本一致，因此其内容可能会落后于各个beta版

## 安装

**历史遗留问题**

如果你之前安装过`nonebot_plugin_ayaka`，请先确保它卸载干净

```
pip uninstall nonebot_plugin_ayaka
```

**安装**

```
pip install ayaka
```

## 作为console程序离线运行

```py
# run.py
import ayaka.adapters.console as cat

# 加载插件
# do something

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```

## 其他

本插件的前身：[nonebot_plugin_ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)
