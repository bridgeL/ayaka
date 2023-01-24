from ayaka import AyakaCat
from pydantic import BaseModel

cat = AyakaCat("人员登记")


# 创建数据对象
class User(BaseModel):
    name: str = ""
    age: int = 0


class UserList(BaseModel):
    users: list[User] = []


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
