'''订阅事件'''


import asyncio


class AyakaSubscribe:
    '''订阅-观察者'''

    def __init__(self) -> None:
        self.async_funcs = {}
        '''必须都是异步方法'''

    def on_change(self, cls_attr):
        '''监听某属性的改变'''
        return self.on(f"{cls_attr}.change")

    def on(self, event_name: str):
        '''注册为某事件的处理回调'''

        def decorator(func):
            '''必须是异步方法'''
            self.async_funcs[event_name] = func
            return func
        return decorator

    async def emit(self, event_name: str, *args, **kwargs):
        '''发送某事件'''
        if event_name in self.async_funcs:
            return await self.async_funcs[event_name](*args, **kwargs)

    def cls_property_watch(self, cls):
        '''监视某个类的属性变换'''
        func = cls.__setattr__

        def new_func(_self, name: str, value) -> None:
            old_value = getattr(self, name, None)
            event_name = f"{cls.__name__}.{name}.change"
            asyncio.create_task(self.emit(event_name, old_value, value, _self))
            func(_self, name, value)

        cls.__setattr__ = new_func
        return cls
