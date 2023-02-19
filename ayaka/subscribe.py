'''订阅事件'''
import asyncio
from ayaka_utils import AyakaSubscribe as BaseAyakaSubscribe
from .context import ayaka_context


class AyakaSubscribe(BaseAyakaSubscribe):
    '''订阅-观察者'''

    def cls_property_watch(self, cls: type):
        '''监视类的属性，其改变时触发事件'''
        old_setter = cls.__setattr__

        def func(_self, name: str, value) -> None:
            old_value = getattr(_self, name, None)
            if old_value is not None and old_value != value:
                event_name = f"{cls.__name__}.{name}.change"
                coro = self.emit(event_name, old_value, value, _self)
                task = asyncio.create_task(coro)
                ayaka_context.wait_tasks.append(task)

            old_setter(_self, name, value)

        cls.__setattr__ = func
        return cls
