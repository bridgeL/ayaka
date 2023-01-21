<div align="center">

# Ayaka - 猫猫，猫猫！ - 0.0.1.4b1

</div>

根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，已支持

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebotv11](https://github.com/nonebot/adapter-onebot)适配器)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其作为console程序离线运行

## 文档

https://bridgel.github.io/ayaka/

## 历史遗留问题

如果你之前安装过`nonebot_plugin_ayaka`，请先确保它卸载干净

```
pip uninstall nonebot_plugin_ayaka
```

## 安装

```
pip install ayaka
```

## 作为console程序离线运行

```py
# run.py
import ayaka.adapters as cat

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
