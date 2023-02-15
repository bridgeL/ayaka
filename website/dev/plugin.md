以赌石为例

```py
# example/stone.py
from random import randint
from ayaka import AyakaCat

cat = AyakaCat("赌石")

cat.set_wakeup_cmds(cmds=["赌石", "stone"])
cat.set_rest_cmds(cmds=["退出", "exit"])

@cat.on_cmd(cmds=["敲", "hit"], states="idle")
async def hit():
    if randint(0, 1):
        return await cat.send("运气真好，开出了和田玉")
    await cat.send("只是一块破石头")
```
## set_wakeup_cmds

```py
cat.set_wakeup_cmds(cmds=["赌石", "stone"])
```

相当于

```py
@cat.on_cmd(cmds=["赌石", "stone"], states="")
async def wakeup():
    await cat.wakeup()
    await cat.send_help()
```

所有`cat`的初始状态都是空，即`cat.state == ""`

当发送`赌石`命令后，若`cat`的状态为`空状态`，将触发该回调

`cat.wakeup`将把cat的状态变为`idle`（默认情况，可设置为其他值），并发送通知，它相当于

```py
cat.state = "idle"
await cat.send("已唤醒猫猫")
```

此时再次发送`赌石`命令，将不会再次触发该回调（因为状态不是空，而是idle）

## set_rest_cmds

```py
cat.set_rest_cmds(cmds=["退出", "exit"])
```

相当于

```py
@cat.on_cmd(cmds=["退出", "exit"], states="*")
async def rest():
    await cat.rest()
```

当发送`退出`命令后，若`cat`的状态为`任意非空状态`，将触发该回调

`cat.rest`将把cat的状态恢复为`空`，并发送通知，它相当于

```py
cat.state = ""
await cat.send("猫猫休息了")
```

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
