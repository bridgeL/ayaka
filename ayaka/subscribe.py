'''订阅事件'''
import asyncio
import inspect
from typing import Callable
from ayaka_utils import is_async_callable, simple_async_wrap
from .context import ayaka_context


class AyakaSubscribeEventCall:
    def __init__(self, func: Callable) -> None:
        if not is_async_callable(func):
            func = simple_async_wrap(func)
        self.func = func
        self.n = len(inspect.signature(func).parameters)

    async def run(self, *args):
        await self.func(*args[:self.n])


class AyakaSubscribe:
    '''订阅-观察者'''

    def __init__(self) -> None:
        self.event_call_dict: dict[str, list[AyakaSubscribeEventCall]] = {}

    def on_change(self, cls_attr):
        '''监听某属性的改变'''
        return self.on(f"{cls_attr}.change")

    def on(self, event_name: str):
        '''注册为某事件的处理回调，同一事件可以注册多个'''
        def decorator(func):
            self.event_call_dict.setdefault(event_name, [])
            self.event_call_dict[event_name].append(
                AyakaSubscribeEventCall(func))
            return func
        return decorator

    async def emit(self, event_name: str, *args):
        '''发送某事件'''
        fs = self.event_call_dict.get(event_name, [])
        ts = [f.run(*args) for f in fs]
        await asyncio.gather(*ts)

    def cls_property_watch(self, cls: type):
        '''监视类的属性，其改变时触发事件'''
        return cls_property_watch(self, cls)


def cls_property_watch(subscribe: AyakaSubscribe, cls: type):
    '''监视类的属性，其改变时触发事件'''
    old_setter = cls.__setattr__

    def func(self, name: str, value) -> None:
        old_value = getattr(self, name, None)
        if old_value is not None and old_value != value:
            event_name = f"{cls.__name__}.{name}.change"
            coro = subscribe.emit(event_name, old_value, value, self)
            task = asyncio.create_task(coro)
            ayaka_context.wait_tasks.append(task)

        old_setter(self, name, value)

    cls.__setattr__ = func
    return cls
