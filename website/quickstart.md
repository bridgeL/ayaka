## 状态机速览

**代码**

```py
# app.py
from ayaka import AyakaCat

cat = AyakaCat("测试一下")


@cat.on_cmd(cmds=["去睡觉", "睡觉吧"], states="")
async def _():
    cat.state = "睡觉"
    await cat.send("睡了喵")


@cat.on_cmd(cmds="起床", states="睡觉")
async def _():
    cat.state = ""
    await cat.send("醒了喵")


@cat.on_cmd(cmds="吃饭", states="")
async def _():
    cat.state = "吃饭"
    await cat.send("吃饭去了")


@cat.on_cmd(cmds=["重置状态", "退出"], states=["吃饭", "睡觉"])
async def _():
    cat.state = ""
    await cat.send("已清空状态")


if __name__ == "__main__":
    from ayaka.adapters.console import run
    run()
```

**命令表（初始状态为空）**

| 状态 | 可用命令             | 下一状态 |
| ---- | -------------------- | -------- |
| 空   | 去睡觉、睡觉吧       | 睡觉     |
| 空   | 吃饭                 | 吃饭     |
| 睡觉 | 起床、重置状态、退出 | 空       |
| 吃饭 | 重置状态、退出       | 空       |


**调试**

```
python app.py
```

在终端输入你的命令进行测试

```
you: 去睡觉
bot: 睡了喵
```

## 作为nb2插件

以上代码可直接放入`src/plugins`中，让nb加载即可
