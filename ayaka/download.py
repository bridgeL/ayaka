'''下载和校验文件hash值'''
import httpx
import hashlib
from pathlib import Path
from pydantic import BaseModel
from .logger import clogger
from .helpers import ensure_dir_exists


class ResItem(BaseModel):
    '''资源项'''
    path: str
    '''下载地址的相对地址尾'''
    hash: str = ""
    '''资源的哈希值'''


class ResInfo(BaseModel):
    '''资源信息'''
    base: str
    '''下载地址的绝对地址头'''
    items: list[ResItem] = []
    '''资源项'''


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
        clogger.info(f"下载文件 <blue>{path}</blue> ...")

    clogger.info(f"拉取数据 <blue>{url}</blue>  ...")
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
        url = res_info.base.rstrip("/") + "/" + item.path.lstrip("/")
        path = base_dir / item.path
        if not path.exists() or (item.hash and get_file_hash(path) != item.hash):
            await resource_download(url, path)
            has_updated = True

    return has_updated
