以赌石为例

```py
# example/stone.py
from random import randint
from ayaka import AyakaCat

# 创建一只猫猫
cat = AyakaCat("赌石")

# 设置唤醒和休息命令
cat.set_wakeup_cmds(cmds=["赌石", "stone"])
cat.set_rest_cmds(cmds=["退出", "exit"])

# 编写业务逻辑
@cat.on_cmd(cmds=["敲", "hit"], states="idle")
async def hit():
    if randint(0, 1):
        return await cat.send("运气真好，开出了和田玉")
    await cat.send("只是一块破石头")
```
## set_wakeup_cmds

`cat.set_wakeup_cmds(cmds=["赌石", "stone"])` 相当于

```py
@cat.on_cmd(cmds=["赌石", "stone"], states="")
async def wakeup():
    '''唤醒猫猫'''
    await cat.wakeup()
    await cat.send_help()
```

而所有`cat`的初始状态都是空，即`cat.state == ""`

当发送`赌石`命令后，`cat`的状态从`空`转为`idle`（wakeup参数默认值），此时再次发送`赌石`命令，将不会再次触发该回调

## set_rest_cmds

`cat.set_rest_cmds(cmds=["退出", "exit"])`相当于

```py
@cat.on_cmd(cmds=["退出", "exit"], states="*")
async def rest():
    '''猫猫休息'''
    await cat.rest()
```

当发送`退出`命令后，若`cat`的状态为`任意非空状态`，将触发该回调

`cat.rest`将把cat的状态恢复为`空`

## hit

```py
@cat.on_cmd(cmds=["敲", "hit"], states="idle")
```

当发送`敲`命令后，若`cat`的状态为`idle`，将触发hit回调，随机一个结果，发送出去

`cat.send`将自动根据上下文，发送到对应的群聊中

若想指定群聊、私聊发送，请使用`cat.send_group`，`cat.send_private`

## 下一步

<div align="right">
    在这里~ ↘
</div>
