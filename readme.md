<div align="center">

# Ayaka - 猫猫，猫猫！ - 0.0.4.7

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ayaka)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ayaka)
![PyPI - License](https://img.shields.io/pypi/l/ayaka)
![PyPI](https://img.shields.io/pypi/v/ayaka)

通过ayaka开发多框架下的、多人互动的群聊插件

</div>

根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，已支持

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebotv11](https://github.com/nonebot/adapter-onebot)适配器，借助[qqguild_patch](https://github.com/mnixry/nonebot-plugin-guild-patch)同时可适配qqguild)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其

- 作为console程序离线运行，便于调试
- 直接通过反向ws连接到gocq上

## 文档

https://bridgel.github.io/ayaka/

## 安装

```
pip install ayaka
```

## 作为console程序离线运行

```
pip install ayaka[fastapi]
```

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

## 直接连接到gocq上

```
pip install ayaka[fastapi]
```

```py
# run2.py
import ayaka.adapters.gocq as cat

# 加载插件
# do something

if __name__ == "__main__":
    cat.run()
```

```
python run2.py
```

## 其他

本插件的前身：[nonebot_plugin_ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)
