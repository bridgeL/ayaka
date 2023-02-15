'''需要先安装ayaka[playwright]'''
from loguru import logger
from typing import Optional
from playwright.async_api import Browser, Playwright, async_playwright, Error
from .adapters import get_adapter

adapter = get_adapter()

_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None


@adapter.on_startup
async def init(**kwargs) -> Browser:
    global _browser
    global _playwright
    _playwright = await async_playwright().start()
    try:
        _browser = await _playwright.chromium.launch(**kwargs)
    except Error:
        await install_browser()
        _browser = await _playwright.chromium.launch(**kwargs)


@adapter.on_shutdown
async def shutdown_browser():
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()  # type: ignore


async def install_browser():
    import os
    import sys
    from playwright.__main__ import main

    os.environ[
        "PLAYWRIGHT_DOWNLOAD_HOST"
    ] = "https://npmmirror.com/mirrors/playwright/"

    # 默认使用 chromium
    sys.argv = ["", "install", "chromium"]

    try:
        os.system("playwright install-deps")
        main()
    except SystemExit as e:
        success = e.code == 0

    if not success:
        logger.error("浏览器更新失败, 请检查网络连通性")


async def get_browser(**kwargs) -> Browser:
    return _browser or await init(**kwargs)
