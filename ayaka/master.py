'''猫猫管理器'''
import time
from .cat import AyakaCat, manager, last_cat_name_dict

cat = AyakaCat("猫猫管理器", overtime=-1)
'''猫猫管理器'''


async def show_relative_cats(name: str):
    '''查找相关猫猫'''
    possibles = []
    for c in manager.cats:
        n = int(len(c.name)/2)
        i = 0
        for w in c.name:
            if w in name:
                i += 1
        if i >= n:
            possibles.append(c.name)
    if possibles:
        await cat.send("你是否是想找猫猫：" + " ".join(possibles))


@cat.on_cmd(cmds="猫猫管理器", always=True, auto_help=False)
async def show_self_help():
    await cat.send_help()


@cat.on_cmd(cmds="帮助", always=True, auto_help=False, block=False)
async def redirect_help():
    cat.cache.setdefault("redirect", True)
    if cat.cache["redirect"]:
        await cat.send("你是在找 [猫猫帮助] 吗\n或者你可以发送 [不要重定向猫猫帮助]，命令我不要回复 [帮助] 指令")


@cat.on_cmd(cmds="不要重定向猫猫帮助", always=True, auto_help=False)
async def set_redirect():
    cat.cache["redirect"] = False
    await cat.send("好的，我知道了")


@cat.on_cmd(cmds=["猫猫帮助", "全部猫猫帮助"], always=True)
async def show_help():
    '''展示猫猫帮助'''
    if cat.cmd == "全部猫猫帮助":
        infos = [c.help for c in manager.cats]
        infos.sort()
        await cat.send_many(infos)
        return

    # 展示指定猫猫的帮助
    if cat.arg:
        name = cat.arg
        c = manager.get_cat(name)
        if c:
            await cat.send(c.help)
        else:
            await cat.send("没有找到对应猫猫")
            await show_relative_cats(name)
        return

    # 只发送已启动的猫猫的帮助
    flag = False
    for c in manager.wakeup_cats:
        await cat.send(c.help)
        flag = True

    if flag:
        return

    # 读取记录
    name, t = last_cat_name_dict.get(cat.session.mark, ["", 0])

    t = int(time.time()) - t
    # 最近猫猫
    if t < 60 and name != cat.name:
        await cat.send(f"您刚刚使用的功能来自猫猫 {name}\n如果想获得进一步帮助请使用命令\n- 猫猫帮助 {name}")
    else:
        # 展示所有猫猫
        infos = []
        for c in manager.cats:
            info = f"- [{c.name}]"
            if not c.valid:
                info += " [已被屏蔽]"
            infos.append(info)
        infos.sort()
        infos = [
            "已加载的猫猫列表",
            *infos,
            "如果想获得进一步帮助请使用命令",
            "- 猫猫帮助 <猫猫名>",
            "- 全部猫猫帮助"
        ]
        await cat.send("\n".join(infos))


@cat.on_cmd(cmds=["屏蔽猫猫", "取消屏蔽猫猫"], always=True)
async def block_cat():
    '''<猫猫名>'''
    if not cat.arg:
        return await cat.send("没有参数")

    name = cat.arg
    if name == cat.name:
        await cat.send("不可屏蔽猫猫管理器")
        return

    c = manager.get_cat(name)
    if not c:
        await cat.send("没有找到对应猫猫")
        await show_relative_cats(name)
        return

    if cat.cmd == "屏蔽猫猫":
        await c.rest()
        c.valid = False
        await cat.send(f"已屏蔽猫猫 {name}")
    else:
        c.valid = True
        await cat.send(f"已取消屏蔽猫猫 {name}")
