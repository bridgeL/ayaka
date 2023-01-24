'''猫猫管理器'''
from .cat import AyakaCat
from .manager import manager


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


@cat.on_cmd(cmds="猫猫帮助", always=True)
async def show_help():
    '''展示猫猫帮助'''
    if cat.arg:
        name = cat.arg
        c = manager.get_cat(name)
        if c:
            await cat.send(c.help)
        else:
            await cat.send("没有找到对应猫猫")
            await show_relative_cats(name)
        return

    flag = False
    for c in manager.cats:
        if c.state:
            await cat.send(c.help)
            flag = True

    if flag:
        return

    infos = ["已加载的猫猫列表"]
    manager.cats.sort(key=lambda x: x.name)
    for c in manager.cats:
        info = f"- [{c.name}]"
        if not c.valid:
            info += " [已被屏蔽]"
        infos.append(info)
    await cat.send("\n".join(infos))

    infos = [
        "如果想获得进一步帮助请使用命令",
        "- 猫猫帮助 <猫猫名>",
        "- 全部猫猫帮助"
    ]
    await cat.send("\n".join(infos))


@cat.on_cmd(cmds="全部猫猫帮助", always=True)
async def show_all_help():
    '''展示展示所有猫猫的帮助'''
    infos = [c.help for c in manager.cats]
    await cat.send_many(infos)


@cat.on_cmd(cmds="猫猫状态", always=True)
async def show_state():
    '''展示猫猫状态'''
    infos = []
    for c in manager.cats:
        if c.state:
            infos.append(f"猫猫 [{c.name}] 状态 [{c.state}] 子状态 [{c.sub_state}]")
    if not infos:
        infos.append("当前没有任何猫猫醒着")
    await cat.send("\n".join(infos))


@cat.on_cmd(cmds="强制休息", always=True)
async def force_exit():
    '''<猫猫名> 强制让猫猫休息'''
    if not cat.arg:
        return await cat.send("请使用 强制休息 <猫猫名>")

    name = cat.arg
    c = manager.get_cat(name)
    if not c:
        await cat.send("没有找到对应猫猫")
        await show_relative_cats(name)
        return

    await c.rest()
    c.remove_private_redirect()


@cat.on_cmd(cmds="屏蔽猫猫", always=True)
async def block_cat():
    '''<猫猫名> 屏蔽猫猫'''
    if not cat.arg:
        return await cat.send("请使用 屏蔽猫猫 <猫猫名>")

    name = cat.arg
    c = manager.get_cat(name)
    if not c:
        await cat.send("没有找到对应猫猫")
        await show_relative_cats(name)
        return

    await c.rest()
    c.valid = False
    await cat.send(f"已屏蔽猫猫 {name}")


@cat.on_cmd(cmds="取消屏蔽猫猫", always=True)
async def unblock_cat():
    '''<猫猫名> 取消屏蔽猫猫'''
    if not cat.arg:
        await cat.send("请使用 取消屏蔽猫猫 <猫猫名>")
        return

    name = cat.arg
    if name == cat.name:
        await cat.send("不可屏蔽猫猫管理器")
        return

    c = manager.get_cat(name)
    if not c:
        await cat.send("没有找到对应猫猫")
        await show_relative_cats(name)
        return

    c.valid = True
    await cat.send(f"已取消屏蔽猫猫 {name}")
