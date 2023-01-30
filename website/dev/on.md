## 注册命令回调

插件最常用的交互模式便是通过命令来交互

### 注册状态命令回调

```py
@cat.on_cmd(cmds="命令A", states="状态1")
async def handle():
    ...
```

**注意：回调必须是无参数的异步方法，ayaka的所有注册回调均是如此！**

你也可以注册多个命令（命令别名），多个状态

```py
@cat.on_cmd(cmds=["命令A", "命令B"], states=["状态1", "状态2"])
async def handle():
    ...
```

### 注册通用状态命令回调

通用状态命令匹配所有状态，在任意状态下均被ayaka接受并响应

```py
@cat.on_cmd(cmds="命令A", states="*")
async def handle():
    ...
```

实际上，`cat.set_rest_cmds(cmds=cmds)`相当于

```py
@cat.on_cmd(cmds=cmds, states="*")
async def rest():
    '''猫猫休息'''
    await cat.rest()
```

### 注册空状态命令回调

大部分时间，你可以使用`cat.set_wakeup_cmds`来设置空状态命令

```py
cat.set_wakeup_cmds(cmds=["猫猫A", "catA"])
```

实际上，`cat.set_wakeup_cmds(cmds=cmds)`相当于

```py
@cat.on_cmd(cmds=cmds)
async def wakeup():
    '''唤醒猫猫'''
    await cat.wakeup()
    await cat.send_help()
```

注：`cat.on_cmd`的`states`参数的缺省值是`""`

因此，你可以自行注册唤醒命令回调，只要保证调用`cat.wakeup`即可

```py
@cat.on_cmd(cmds=["猫猫A", "catA"])
async def wakeup():
    await cat.wakeup()
    await cat.send("喵~")
```

当然，你甚至可以不调用`cat.wakeup`

这会导致这条命令并不会唤醒猫猫，令其状态保持为空状态

## 注册子状态命令回调

```py
@cat.on_text(state="idle", sub_states="name")
async def _():
    # do something
```

该回调会在群状态为`idle`，群成员状态为`name`时响应

## 注册文字回调

与命令回调同理，只是不需要再写cmds了

## 高级

### always

默认值 False

设置为True，则该回调必定触发，不受ayaka各类状态规则的约束，并且执行优先级最高

### auto_help

默认值 True

设置为False，则禁止对该回调生成猫猫帮助

### block

是否阻断消息传播

默认值：命令回调 阻断，文字回调 不阻断

### 处理顺序

消息传播依次经过

- always 命令回调
- always 文字回调
- 命令回调
- 文字回调

期间任意回调block为True或抛出`BlockException`都会导致消息传播的结束

## 钩子函数

```py
from ayaka import get_adapter

adapter = get_adapter()

@adapter.on_startup
async def func():
    print("hi")
```

func将在asgi服务启动后，发送hi

## 下一步

<div align="right">
    在这里~ ↘
</div>
