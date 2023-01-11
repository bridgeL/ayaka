import sys
keys = list(sys.modules.keys())


def has_been_imported(module_name: str):
    for k in keys:
        ks = k.split(".")
        if module_name in ks:
            return True
    return False


if has_been_imported("hoshino"):
    print("智能识别选择 hoshino")
    from .hoshino import init, run, regist
elif has_been_imported("nonebot"):
    if has_been_imported("onebot"):
        print("智能识别选择 onebot v11")
        from .onebot import init, run, regist
else:
    print("智能识别选择 console")
    from .console import init, run, regist
