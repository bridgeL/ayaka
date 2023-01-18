## 赌石

```py
# example/stone.py
from random import randint
from ayaka import AyakaCat

# 创建一只猫猫
cat = AyakaCat("赌石")

# 设置唤醒和休息命令
cat.set_wakeup_cmds(cmds=["赌石", "stone"])
cat.set_rest_cmds(cmds=["退出", "exit"])
```

```py
# 编写业务逻辑
@cat.on_cmd(cmds=["敲", "hit"], states="idle")
async def hit():
    if randint(0, 1):
        return await cat.send("运气真好，开出了和田玉")
    await cat.send("只是一块破石头")
```

## 敲木鱼

```py
# example/muyu.py
from ayaka import AyakaCat
from pydantic import BaseModel

# 创建一只猫猫
cat = AyakaCat("木鱼")

# 设置唤醒和休息命令
cat.set_wakeup_cmds(cmds=["木鱼", "muyu"])
cat.set_rest_cmds(cmds=["退出", "exit"])
```

```py
# 创建数据对象
class User(BaseModel):
    id: str
    name: str
    cnt: int = 0


class Muyu(BaseModel):
    users: list[User] = []
    step: int = 1

    def get(self, user_id: str, user_name: str):
        for user in self.users:
            if user.id == user_id:
                return user
        else:
            user = User(id=user_id, name=user_name)
            self.users.append(user)
        return user

    def hit(self, user_id: str, user_name: str):
        user = self.get(user_id, user_name)
        user.cnt += self.step
```

```py
# 编写业务逻辑
@cat.on_cmd(cmds=["敲", "hit"], states="idle")
async def hit():
    muyu = cat.get_data(Muyu)
    muyu.hit(cat.user.id, cat.user.name)
    await cat.send("笃")


@cat.on_cmd(cmds=["查询功德", "query"], states="idle")
async def query():
    muyu = cat.get_data(Muyu)
    user = muyu.get(cat.user.id, cat.user.name)
    await cat.send(f"[{user.name}] 现在的功德是 {user.cnt}")


@cat.on_cmd(cmds=["调整步进", "set step"], states="idle")
async def set_step():
    if not cat.nums:
        return await cat.send("没有输入数字")
    muyu = cat.get_data(Muyu)
    muyu.step = cat.nums[0]
```

## 离线调试

```py
# run.py
import ayaka.adapters as cat

# 加载插件
from example import stone
from example import muyu

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```

## 调用测试脚本

```
# 执行全部测试
s 0

# 测试木鱼
s muyu

# 测试赌石
s stone
```

## 猫猫帮助

<div class="demo">
"user" 说：猫猫帮助
"Bot" 说：加载的猫猫列表
- [木鱼]
- [猫猫管理器]
- [赌石]
"Bot" 说：如果想获得进一步帮助请使用命令
- 猫猫帮助 - &lt;猫猫名>
- 全部猫猫帮助
</div>

<div class="demo">
"user" 说：猫猫帮助 赌石
"Bot" 说：[赌石]
- 赌石/stone 唤醒猫猫
[*]
- 退出/exit 猫猫休息
[idle]
- 敲/hit
</div>

<div class="demo">
"user" 说：猫猫帮助 木鱼
"Bot" 说：[木鱼]
- 木鱼/muyu 唤醒猫猫
[*]
- 退出/exit 猫猫休息
[idle]
- 敲/hit
- 查询功德/query
- 调整步进/set step
</div>

## 避免命令碰撞

以上两个插件可以同时工作，不担心`敲/hit`命令碰撞

这是因为它们属于不同的猫猫，在不同的碰撞域中，不会发生碰撞冲突

### 赌石

| 命令           | 什么状态下可用 |
| -------------- | -------------- |
| **赌石/stone** | **未唤醒**     |
| 退出/exit      | 任意状态       |
| 敲/hit         | idle           |

### 木鱼

| 命令              | 什么状态下可用 |
| ----------------- | -------------- |
| **木鱼/muyu**     | **未唤醒**     |
| 退出/exit         | 任意状态       |
| 敲/hit            | idle           |
| 查询功德/query    | idle           |
| 调整步进/set step | idle           |

### 唤醒命令

**所有的唤醒命令都位于同一碰撞域**，它们之间需要注意相互的唯一性

也就是说，需要保证`赌石/stone`与`木鱼/muyu`不重复

所有的状态命令都从属于某只猫猫，而不同猫猫的状态命令间不会发生碰撞

因为当一只猫猫被唤醒后，所有其他猫猫的唤醒命令+状态命令都将被ayaka拒绝

ayaka此时仅接受当前猫猫的状态命令

### idle状态

猫猫被唤醒后，默认进入idle状态

此时ayaka将拒绝所有其他状态下的命令

但是有一种特殊命令除外，那就是`*`命令，它匹配所有状态，在任意状态下均不会被ayaka拒绝

## 便利的数据缓存

ayaka为每个群聊均设置了一份字典

各个插件中的猫猫均可以通过`cat.cache`访问到该字典中的一部分空间：

```
cat.cache <-> total_dict[group_id][cat.name]
```

各个猫猫获取到的空间是相互独立的，不会发生冲突

同时，ayaka还设计了`cat.get_data`、`cat.pop_data`方法读写`cat.cache`

可以将`BaseModel`放入其中使用，解决了直接读写字典时缺乏类型提示的问题

注意：缓存数据会在bot重启后丢失

## 下一步

<div align="right">
    在这里~ ↘
</div>
