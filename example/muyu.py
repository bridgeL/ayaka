'''def 电子木鱼(敲) -> 电子功德'''
from ayaka import AyakaCat
from pydantic import BaseModel

# 创建一只猫猫
cat = AyakaCat("木鱼")

# 设置唤醒和休息命令
cat.set_wakeup_cmds(cmds=["木鱼", "muyu"])
cat.set_rest_cmds(cmds=["退出", "exit"])


# 创建数据对象
class User(BaseModel):
    id: str
    name: str
    cnt: int = 0


class Muyu(BaseModel):
    users: list[User] = []
    step: int = 1

    def get(self, user_id: str):
        for user in self.users:
            if user.id == user_id:
                return user.cnt
        return 0

    def hit(self, user_id: str, user_name: str):
        for user in self.users:
            if user.id == user_id:
                break
        else:
            user = User(id=user_id, name=user_name)
            self.users.append(user)
        user.cnt += self.step


# 编写业务逻辑
@cat.on_cmd(cmds=["敲", "hit"], states="idle")
async def hit():
    muyu = cat.get_data(Muyu)
    muyu.hit(cat.user.id, cat.user.name)
    await cat.send("笃")


@cat.on_cmd(cmds=["查询功德", "query"], states="idle")
async def query():
    muyu = cat.get_data(Muyu)
    virtue = muyu.get(cat.user.id)
    await cat.send(f"[{cat.user.name}] 现在的功德是 {virtue}")


@cat.on_cmd(cmds=["调整步进", "set step"], states="idle")
async def set_step():
    if not cat.nums:
        return await cat.send("没有输入数字")
    muyu = cat.get_data(Muyu)
    muyu.step = cat.nums[0]
