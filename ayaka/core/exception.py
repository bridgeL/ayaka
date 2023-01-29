'''
    提供各类报错
'''


class NotRegistrationError(Exception):
    def __init__(self, async_func_name: str) -> None:
        super().__init__(f"{async_func_name} 方法未注册！")


class DuplicateCatNameError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"{name} 猫猫重名！")


class DuplicateRegistrationError(Exception):
    def __init__(self, async_func_name: str) -> None:
        super().__init__(f"{async_func_name} 方法重复注册！")


class BlockException(Exception):
    def __init__(self) -> None:
        super().__init__("阻断后续事件传播")


class NotBlockException(Exception):
    def __init__(self) -> None:
        super().__init__("放弃阻断后续事件传播")
