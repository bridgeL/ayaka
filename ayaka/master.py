'''猫猫管理器'''
from .cat import AyakaCat, manager


cat = AyakaCat("猫猫管理器")
'''猫猫管理器'''


@cat.on_cmd(cmds="猫猫管理器", always=True, auto_help=False)
async def show_self_help():
    await cat.send_help()


@cat.on_cmd(cmds="猫猫列表", always=True)
async def list_cat():
    '''展示所有猫猫'''
    infos = ["已加载的猫猫列表"]
    for c in manager.cats:
        info = f"- [{c.name}]"
        if not c.valid:
            info += " [已被屏蔽]"
        infos.append(info)
    await cat.send("\n".join(infos))


async def show_relative_cats(name: str):
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


@cat.on_cmd(cmds="帮助", always=True, auto_help=False)
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
    if cat.params.arg:
        name = cat.params.arg
        c = manager.get_cat(name)
        if c:
            await cat.send(c.help)
        else:
            await cat.send("没有找到对应猫猫")
            await show_relative_cats(name)
        return

    c = cat.current.cat
    if c:
        await cat.send(c.help)
        return

    await list_cat()
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
    c = cat.current.cat
    if c:
        info = f"当前猫猫[{c.name}]\n当前状态[{c.state}]"
    else:
        info = "当前没有任何猫猫醒着"
    await cat.send(info)


@cat.on_cmd(cmds="强制退出", always=True)
async def force_exit():
    '''强制让当前猫猫休息'''
    c = cat.current.cat
    if c:
        await c.rest()


@cat.on_cmd(cmds="屏蔽猫猫", always=True)
async def block_cat():
    '''<猫猫名> 屏蔽猫猫'''
    if not cat.params.arg:
        await cat.send("请使用 屏蔽猫猫 <猫猫名>")
        return

    name = cat.params.arg
    c = manager.get_cat(name)
    if not c:
        await cat.send("没有找到对应猫猫")
        await show_relative_cats(name)
        return

    await c.close()
    c.valid = False
    await cat.send(f"已屏蔽猫猫 {name}")


@cat.on_cmd(cmds="取消屏蔽猫猫", always=True)
async def unblock_cat():
    '''<猫猫名> 取消屏蔽猫猫'''
    if not cat.params.arg:
        await cat.send("请使用 取消屏蔽猫猫 <猫猫名>")
        return

    name = cat.params.arg
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
