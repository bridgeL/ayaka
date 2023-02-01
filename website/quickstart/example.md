## 准备工作

下载本仓库

```
git clone https://github.com/bridgeL/ayaka.git
```

使用[poetry](https://python-poetry.org/docs/)安装依赖

```
poetry shell
poetry install
```

**本页的示例均可在其example中找到**

## 示例插件

### 赌石

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

### 敲木鱼

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

### 人员登记

```py
# example/input.py
from ayaka import AyakaCat
from pydantic import BaseModel

cat = AyakaCat("人员登记")
```

```py
# 创建数据对象
class User(BaseModel):
    name: str = ""
    age: int = 0


class UserList(BaseModel):
    users: list[User] = []
```

```py
# 编写业务逻辑
@cat.on_cmd(cmds="查看登记情况")
async def show():
    # 展示总表
    user_list = cat.get_data(UserList)
    items = [repr(u) for u in user_list.users]
    await cat.send_many(items)


@cat.on_cmd(cmds="我要登记")
async def start():
    # 下一阶段
    cat.sub_state = "name"
    await cat.send("姓名")


@cat.on_text(sub_states="name")
async def input_name():
    # 记录数据
    user = cat.user.get_data(User)
    user.name = cat.arg
    
    # 下一阶段
    cat.sub_state = "age"
    await cat.send("年龄")


@cat.on_text(sub_states="age")
async def input_age():
    # 从缓存中清除
    user = cat.user.pop_data(User)
    user.age = cat.arg

    # 复原状态
    cat.sub_state = ""

    # 记录到总表
    user_list = cat.get_data(UserList)
    user_list.users.append(user)

    # 展示
    await cat.send(f"登记完成 {user}")
```

## 离线调试

### 作为console程序运行

```py
# run.py
import ayaka.adapters as cat

# 加载插件
from example import stone
from example import muyu
from example import input

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```

### 编写测试脚本

```
# script/muyu.txt
# 测试木鱼 √

g 100 1 木鱼
g 100 1 敲
g 100 1 敲
g 100 1 查询功德
g 100 1 set step 1000
g 100 1 hit
g 100 1 query
g 100 1 exit
```

```
# script/stone.txt
# 测试赌石 √

# 设定默认角色
g 100 1 

# 接下来均以群聊100中的uid为1的角色来发言
赌石
敲
敲
hit
hit
exit
```

```
# script/input.txt
g 100 1 我要登记
g 100 1 江山
g 100 1 12
g 100 2 我要登记
g 100 2 明月
g 100 3 我要登记
g 100 1 查看登记情况
g 100 3 红袖 
g 100 2 100
g 100 3 18
g 100 1 查看登记情况
```

```
# script/0.txt
# 测试木鱼
s muyu

# 测试赌石
s stone

# 测试人员登记
s input
```

### 运行测试脚本

```
python run.py
```

然后

```
s 0
```

## 猫猫帮助

ayaka自动为以上三个插件生成了帮助

<div class="demo">
"user" 说：猫猫帮助
"Bot" 说：加载的猫猫列表
- [人员登记]
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
猫猫插件：赌石
[*]
- 退出/exit 猫猫休息
- 赌石/stone 唤醒猫猫
[idle]
- 敲/hit
</div>

<div class="demo">
"user" 说：猫猫帮助 木鱼
"Bot" 说：[木鱼]
猫猫插件：木鱼
[*]
- 退出/exit 猫猫休息
- 木鱼/muyu 唤醒猫猫
[idle]
- 敲/hit
- 查询功德/query
- 调整步进/set step
</div>

<div class="demo">
"user" 说：猫猫帮助 人员登记
"Bot" 说：[人员登记]
猫猫插件：人员登记
- 查看登记情况
- 我要登记
[age]
-  &lt;任意文字>
[name]
-  &lt;任意文字>
</div>

## 下一步

<div align="right">
    在这里~ ↘
</div>
