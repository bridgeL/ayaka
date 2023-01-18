## 注册命令回调

插件最常用的交互模式便是通过命令来交互

通过前文可知，ayaka中的命令具有两类：唤醒命令、状态命令

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

通用状态命令匹配所有状态，在任意状态下均不会被ayaka拒绝

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

### 注册唤醒命令回调

大部分时间，你可以使用`cat.set_wakeup_cmds`来设置唤醒命令

```py
cat.set_wakeup_cmds(cmds=["猫猫A", "catA"])
```

但有时，你喜欢在唤醒猫猫的时候做些其他的事情

其实，唤醒命令在形式上是一种特殊的状态命令，它注册在`""`（空字符串）状态下

`cat.on_cmd`的`states`参数的缺省值便是`""`

实际上，`cat.set_wakeup_cmds(cmds=cmds)`相当于

```py
@cat.on_cmd(cmds=cmds)
async def wakeup():
    '''唤醒猫猫'''
    await cat.wakeup()
    await cat.send_help()
```

因此，你可以自行注册唤醒命令回调，只要保证调用`cat.wakeup`即可

```py
@cat.on_cmd(cmds=["猫猫A", "catA"])
async def wakeup():
    await cat.wakeup()
    await cat.send("喵~")
```

当然，你甚至可以不调用`cat.wakeup`

这会导致这条命令并不会唤醒猫猫，从而维持**没有任何猫猫被唤醒**的情形

### 注册混合命令回调

唤醒命令在形式上是一种特殊的状态命令，这一特性带来了特定的好处

例如，有些时候，你希望猫猫在未唤醒和唤醒状态下，收到同一条命令时，执行相同操作（`喵~`）

那么你可以

```py
@cat.on_cmd(cmds=["猫猫A", "catA"], states=["", "idle"])
async def wakeup():
    await cat.wakeup()
    await cat.send("喵~")
```

不用担心`cat.wakeup`重复调用的问题，它仅在猫猫未唤醒时才会真正执行，唤醒后执行该语句会直接返回

## 注册文字回调

### 注册状态文字回调

文字回调往往是注册在某个状态下生效，当猫猫处于该状态时，任意消息都会触发该状态下的文字回调，进行相关处理

```py
@cat.on_text(states="idle")
async def handle():
    ...
```

### 注册通用状态文字回调

同样的，文字回调也可以注册为通用状态，不过这种用法并不常见

```py
@cat.on_text(states="*")
async def handle():
    ...
```

### 注册唤醒文字回调

```py
@cat.on_text()
async def handle():
    ...
```

这并不是一个清晰的表述，仅仅用于表现其与唤醒命令回调的某些**相似之处**

实际上，所谓唤醒命令回调、唤醒文字回调，都是指那些在**没有任何猫猫被唤醒**的情形下，可被ayaka响应的回调

状态命令回调、状态文字回调，均是需要在其**从属的猫猫被唤醒**后，且**状态匹配**的时候才能被ayaka响应

### 注册混合文字回调

与混合命令回调同理

在某些特殊情况下会很有用

```py
@cat.on_text(states=["", "*"])
async def handle():
    ...
```

## 高级

always（必定触发，不受ayaka各类状态规则的约束，并且执行优先级最高）

channel_types（可能会留到新章节介绍）

### block

是否阻断消息传播

命令回调默认阻断

文字回调默认不阻断

### 处理顺序

消息传播依次经过

- always 命令回调
- always 文字回调
- 唤醒命令/状态命令回调
- 文字回调

期间任意回调block为True或抛出`BlockException`都会导致消息传播的结束

## 下一步

<div align="right">
    在这里~ ↘
</div>
