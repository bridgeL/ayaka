'''订阅事件'''


class AyakaSubscribe:
    '''订阅-观察者'''
    
    def __init__(self) -> None:
        self.funcs = {}
        '''必须都是异步方法'''

    def on(self, name: str):
        '''注册为某事件的处理回调'''
        def decorator(func):
            '''必须是异步方法'''
            self.funcs[name] = func
            return func
        return decorator

    async def emit(self, name: str, *args, **kwargs):
        '''发送某事件'''
        return await self.funcs[name](*args, **kwargs)
