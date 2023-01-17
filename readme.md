<div align="center">

# Ayaka - 猫猫，猫猫！ - 0.0.0.5b3

</div>

根据py包的导入情况，猜测当前插件工作在哪个机器人框架下，已支持

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebotv11](https://github.com/nonebot/adapter-onebot)适配器)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

## 历史遗留问题

如果你之前安装过`nonebot_plugin_ayaka`，请先确保它卸载干净

```
pip uninstall nonebot_plugin_ayaka
```

## 安装

```
pip install ayaka
```

## 配置

### 必须满足的要求

1. 已配置command_start、command_sep
2. command_start、command_sep 均只有一项
3. command_sep 不为空字符串

ayaka仅保证在此限制下正常工作

### 推荐配置

```
command_start = [""]
command_sep = [" "]
```

## 其他

本插件的前身：[nonebot_plugin_ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)
