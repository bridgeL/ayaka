'''订阅事件'''
import asyncio
import inspect
from typing import Awaitable, Callable
from .context import get_context

ASYNC_FUNC = Callable[..., Awaitable]
'''异步方法'''


class AyakaSubscribe:
    '''订阅-观察者'''

    def __init__(self) -> None:
        self.async_funcs: dict[str, list[tuple[ASYNC_FUNC, int]]] = {}
        '''必须都是异步方法'''

    def on_change(self, cls_attr):
        '''监听某属性的改变'''
        return self.on(f"{cls_attr}.change")

    def on(self, event_name: str):
        '''注册为某事件的处理回调'''

        def decorator(async_func):
            '''必须是异步方法'''
            if event_name not in self.async_funcs:
                self.async_funcs[event_name] = []

            s = inspect.signature(async_func)
            n = len(s.parameters)
            self.async_funcs[event_name].append([async_func, n])
            return async_func

        return decorator

    async def emit(self, event_name: str, *args):
        '''发送某事件'''
        if event_name in self.async_funcs:
            items = self.async_funcs[event_name]
            await asyncio.gather(*[
                async_func(*args[:n])
                for async_func, n in items
            ])

    def cls_property_watch(self, cls):
        '''监视类的属性，其改变时触发事件'''
        func = cls.__setattr__

        def new_func(c_self, name: str, value) -> None:
            old_value = getattr(c_self, name, None)
            if old_value is not None and old_value != value:
                event_name = f"{cls.__name__}.{name}.change"
                task = asyncio.create_task(
                    self.emit(event_name, old_value, value, c_self))
                context = get_context()
                context.wait_tasks.append(task)

            func(c_self, name, value)

        cls.__setattr__ = new_func
        return cls
