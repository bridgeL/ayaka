'''提供一些有益的方法和类'''
import asyncio
import hashlib
import inspect
import json
import httpx
import functools
from time import time
from pathlib import Path
from loguru import logger
from .model import ResInfo


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


async def download_url(url: str) -> bytes:
    '''返回指定链接下载的字节流数据'''
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20)
        resp.raise_for_status()
        return resp.content


async def resource_download(url: str, path: str | Path = ""):
    '''异步下载资源到指定位置

    下载资源时，若给定的文件地址的父目录不存在，则会自动新建，无需担心找不到目录的异常

    参数：

        url：资源网址

        path：本地下载位置

    返回：

        下载得到的字节数据

    异常：

        下载异常
    '''
    if path:
        path = ensure_dir_exists(path)
        logger.opt(colors=True).info(f"下载文件 <blue>{path}</blue> ...")

    logger.opt(colors=True).info(f"拉取数据 <blue>{url}</blue>  ...")
    data = await download_url(url)

    # 保存
    if path:
        path.write_bytes(data)

    return data


def get_file_hash(path: str | Path, force_LF: bool = True):
    '''获取文件的hash值

    参数：

        path：文件地址

        force_LF：强制替换文件中的换行符为\\n

    返回：

        16进制哈希值
    '''
    path = ensure_dir_exists(path)
    data = path.read_bytes()
    if force_LF:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.md5(data).hexdigest()


async def resource_download_by_res_info(res_info: ResInfo, base_dir: str | Path):
    '''根据res_info，异步下载资源到指定位置，只下载哈希值发生变化的资源项

    下载资源时，若给定的文件地址的父目录不存在，则会自动新建，无需担心找不到目录的异常

    参数：

        res_info：资源信息

        base_dir：本地文件地址

    返回：

        是否存在更新
    '''
    if isinstance(base_dir, str):
        base_dir = Path(base_dir)

    has_updated = False
    for item in res_info.items:
        url = res_info.base + "/" + item.path
        path = base_dir / item.path
        if not path.exists() or get_file_hash(path) != item.hash:
            await resource_download(url, path)
            has_updated = True

    return has_updated


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
