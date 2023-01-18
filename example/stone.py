'''赌石'''
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
