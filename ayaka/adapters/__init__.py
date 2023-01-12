import sys
keys = list(sys.modules.keys())


def has_been_imported(module_name: str):
    for k in keys:
        ks = k.split(".")
        if module_name in ks:
            return True
    return False

# hoshino
if has_been_imported("hoshino"):
    print("智能识别 hoshino，加载为hoshino插件")
    from .hoshino import regist
    regist()
    
# nonebot
elif has_been_imported("nonebot"):
    is_nonebot2 = False
    try:
        from nonebot import NoneBot
    except:
        is_nonebot2 = True
    else:
        # nonebot1
        pass

    # nonebot2
    if is_nonebot2:
        # onebot
        if has_been_imported("onebot"):
            print("智能识别 nonebot2 onebot v11，加载为nonebot2插件")
            from .nonebot2.onebot import regist
            regist()
        
        # 其他
        else:
            print("暂不支持nonebot2其他适配器")
    
    # nonebot1
    else:
        print("智能识别 nonebot1，加载为nonebot1插件")
        from .nonebot1 import regist
        regist()

# console
else:
    print("智能识别 console，请手动执行init、regist、run函数")
    from .console import init, regist, run
