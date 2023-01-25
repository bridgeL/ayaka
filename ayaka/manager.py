'''保存和管理所有猫猫，处理事件分发'''
import asyncio
from typing import TYPE_CHECKING
from .exception import DuplicateCatNameError
from .event import AyakaEvent
from .context import set_context
from .bridge import bridge
from .trigger import AyakaTrigger

if TYPE_CHECKING:
    from .cat import AyakaCat


async def run_triggers(ts: list[AyakaTrigger]):
    # 遍历尝试执行
    for t in ts:
        if await t.run():
            return


class AyakaManager:
    '''分发ayaka event'''

    def __init__(self) -> None:
        self.cats: list["AyakaCat"] = []
        '''所有猫猫'''
        self.private_redirect_dict: dict[str, list[str]] = {}
        '''将私聊消息转发至群聊，dict[private_id: list[group_id]]'''

    @property
    def wakeup_cats(self):
        '''所有不处于空状态的猫猫'''
        return [c for c in self.cats if c.state]

    async def handle_event(self, event: AyakaEvent):
        '''处理和转发事件'''
        # 设置上下文
        set_context(event)

        # 获取碰撞域中的触发器
        ts_list = [c.get_triggers() for c in self.cats]
        
        # for ts in ts_list:
        #     for t in ts:
        #         print(t)
        #     print()

        # 同时执行
        tasks = [
            asyncio.create_task(run_triggers(ts))
            for ts in ts_list if ts
        ]
        await asyncio.gather(*tasks)

        # 排除已经转发的情况
        if event.private_forward_id:
            return

        # 转发私聊消息到群聊
        if event.session_type == "private":
            private_id = event.session_id
            group_ids = self.private_redirect_dict.get(private_id, [])

            for group_id in group_ids:
                # 私聊消息转为群聊消息
                _event = event.copy()
                _event.session_type = "group"
                _event.session_id = group_id
                _event.private_forward_id = private_id

                await self.handle_event(_event)

    def add_cat(self, cat: "AyakaCat"):
        for c in self.cats:
            if c.name == cat.name:
                raise DuplicateCatNameError(cat.name)
        self.cats.append(cat)

    def get_cat(self, name: str):
        for c in self.cats:
            if c.name == name:
                return c

    # ---- 监听 ----
    def add_private_redirect(self, group_id: str, private_id: str):
        if private_id not in self.private_redirect_dict:
            self.private_redirect_dict[private_id] = [group_id]
        elif group_id not in self.private_redirect_dict[private_id]:
            self.private_redirect_dict[private_id].append(group_id)

    def remove_private_redirect(self, group_id: str, private_id: str = ""):
        # 移除所有监听
        if not private_id:
            empty_private_ids = []

            # 遍历监听表
            for private_id, group_ids in self.private_redirect_dict.items():
                # 移除监听
                if group_id in group_ids:
                    group_ids.remove(group_id)

                # 统计所有无监听者的目标
                if not group_ids:
                    empty_private_ids.append(private_id)

            # 移除这些无监听者的目标
            for private_id in empty_private_ids:
                self.private_redirect_dict.pop(private_id)

        # 移除指定监听
        else:
            group_ids = self.private_redirect_dict.get(private_id, [])

            # 移除监听
            if group_id in group_ids:
                group_ids.remove(group_id)

            # 移除无监听者的目标
            if not group_ids:
                self.private_redirect_dict.pop(private_id)


manager = AyakaManager()

# 注册内部服务
bridge.regist(manager.handle_event)
