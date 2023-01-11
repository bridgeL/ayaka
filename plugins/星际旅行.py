# ---------- 1 ----------
from ayaka import AyakaCat

cat = AyakaCat("星际旅行")
cat.help = "xing ji lv xing"

# 启动猫猫
cat.set_start_cmds(cmds=["星际旅行", "travel"])
# 关闭猫猫
cat.set_close_cmds(cmds=["退出", "exit"])

# ---------- 2 ----------
@cat.on_cmd(cmds="move", states="*")
async def move():
    '''移动'''
    cat.state = cat.params.arg
    await cat.send(f"前往 {cat.state}")
    
# ---------- 3 ----------
@cat.on_cmd(cmds="hi", states=["地球", "月球", "太阳"])
async def say_hi():
    '''打招呼'''
    await cat.send(f"你好，{cat.state}！")

# ---------- 4 ----------
# 相同命令，不同行为
@cat.on_cmd(cmds="drink", states=["地球", "月球"])
async def drink():
    '''喝水'''
    await cat.send("喝水")

@cat.on_cmd(cmds="drink", states="太阳")
async def drink():
    '''喝太阳风'''
    await cat.send("喝太阳风")

# ---------- 5 ----------
from pydantic import BaseModel

class Cache(BaseModel):
    ticket:int = 0

@cat.on_cmd(cmds=["buy", "买票"], states="售票处")
async def buy_ticket():
    '''买门票'''
    cache = cat.get_data(Cache)
    cache.ticket += 1
    await cat.send("耀斑表演门票+1")

@cat.on_cmd(cmds=["watch", "看表演"], states="*")
async def watch():
    '''看表演'''
    cache = cat.get_data(Cache)
    if cache.ticket <= 0:
        await cat.send("先去售票处买票！")
    else:
        cache.ticket -= 1
        await cat.send("门票-1")
        await cat.send("10分甚至9分的好看")

# ---------- 6 ----------
@cat.on_text(states="火星")
async def handle():
    '''令人震惊的事实'''
    await cat.send("你火星了")

# ---------- 7 ----------
from ayaka import AyakaConfig

class Cache2(BaseModel):
    gold:int = 0

class Config(AyakaConfig):
    __config_name__ = cat.name
    gold_each_time: int = 1

config = Config()

@cat.on_cmd(cmds="pick", states="沙城")
async def get_gold():
    '''捡金子'''
    cache = cat.get_data(Cache2)
    cache.gold += config.gold_each_time
    await cat.send(f"+{config.gold_each_time} / {cache.gold}")

# ---------- 8 ----------
@cat.on_cmd(cmds="change", states="沙城")
async def change_gold_number():
    '''修改捡金子配置'''
    config = Config()
    config.gold_each_time = cat.params.nums[0]
    await cat.send(f"修改每次拾取数量为{config.gold_each_time}")
