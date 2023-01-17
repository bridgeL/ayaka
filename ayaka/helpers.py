'''提供一些有益的方法和类'''
import asyncio
import inspect
import json
import functools
from time import time
from pathlib import Path


def ensure_list(data: str | list | tuple | set):
    '''确保为列表'''
    if isinstance(data, str):
        return [data]
    if isinstance(data, list):
        return data
    return list(data)


def ensure_dir_exists(path: str | Path):
    '''确保目录存在

    参数：

        path：文件路径或目录路径

            若为文件路径，该函数将确保该文件父目录存在

            若为目录路径，该函数将确保该目录存在

    返回：

        Path对象
    '''
    if not isinstance(path, Path):
        path = Path(path)
    # 文件
    if path.suffix:
        ensure_dir_exists(path.parent)
    # 目录
    elif not path.exists():
        path.mkdir(parents=True)
    return path


async def do_nothing():
    '''什么也不做，可以当个占位符'''
    pass


def singleton(cls):
    '''单例模式的装饰器'''
    instance = None

    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return getinstance


class Timer:
    '''计时器

    示例代码:
    ```
        with Timer("test"):
            # some code...

        # 输出：[test] 耗时2.02s
    ```
    '''

    def __init__(self, name: str = "", show: bool = True) -> None:
        self.name = name
        self.diff = 0
        self.show = show

    def __enter__(self):
        self.time = time()

    def __exit__(self, a, b, c):
        self.diff = time() - self.time
        if self.show:
            print(f"[{self.name}] 耗时{self.diff:.2f}s")


def load_data_from_file(path: str | Path):
    '''从指定文件加载数据

    参数:

        path: 文件路径

        若文件类型为json，按照json格式读取

        若文件类型为其他，则按行读取，并排除空行

    返回:

        json反序列化后的结果(对应.json文件) 或 字符串数组(对应.txt文件)
    '''
    path = ensure_dir_exists(path)
    if not path.exists():
        raise Exception(f"文件不存在 {path}")

    with path.open("r", encoding="utf8") as f:
        if path.suffix == ".json":
            return json.load(f)
        else:
            # 排除空行
            return [line.strip() for line in f if line.strip()]


def is_async_callable(obj) -> bool:
    '''抄自 starlette._utils.is_async_callable

    判断对象是否可异步调用'''
    while isinstance(obj, functools.partial):
        obj = obj.func

    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(obj.__call__)
    )


def debug_print(*args):
    '''快速插桩'''
    t = inspect.stack()[1]
    items = [
        "---- debug_print ----",
        f"File \"{t.filename}\", line {t.lineno}, when running",
        t.code_context[0].rstrip()
    ]
    print("\n".join(items))
    print(*args, "\n")


def simple_repr(obj: object, exclude: set[str] = set(), **params):
    '''快速获得一份简单的对象repr'''
    # 复制一份，防止update修改原内容
    data = {k: v for k, v in vars(obj).items() if k not in exclude}
    data.update(params)
    data = ", ".join(f"{k}={v}" for k, v in data.items())
    return f"{obj.__class__.__name__}({data})"
