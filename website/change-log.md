## 0.0.0.1

喵，从nonebot_plugin_ayaka发源

### 0.0.0.4

第一个可用版本

- 新特性：可适配 nb1、nb2、hoshino 机器人框架
- 新特性：通过state可实现对群状态的控制
- 新特性：通过cache可实现对群缓存数据的控制

### 0.0.0.5

- 新特性：可作为console程序离线运行
- 新特性：取消separate、prefix只取第一项的限制
- 新特性：提供下载和校验文件支持
- 新特性：nb2ob11适配器在发送消息失败后自动发送失败提示消息
- 新特性：报错信息保存至data/ayaka/error.log中
- 修复BUG：nb2适配器中ayaka_event中的字符串未转义回正常格式

## 0.0.1.0

- 破坏性变更：修改ayaka_event结构，新增AyakaSender，更新所有适配器
- 破坏性变更：删除bridge.ready
- 破坏性变更：删除AyakaCurrent，其原本功能合并至AyakaManager，AyakaCat新增多个计算属性
- 破坏性变更：AyakaSession更名为AyakaChannel，更新所有适配器
- 破坏性变更：AyakaEvent新增at、reply字段，更新所有适配器
- 破坏性变更：删除旧orm，使用sqlmodel
- 破坏性变更：User更名为GroupMember，所有适配器已更新
- 修复BUG：特定情况下，AyakaParams无法正确解析参数
- 修复BUG：猫猫管理器无法正确工作
- 新增依赖：sqlmodel
- 新增文档：本站

### 0.0.1.2

- 新特性：新增handle_event方法
- 新特性：优化base_send_many方法，令其支持私聊

### 0.0.1.3

- 优化代码

### 0.0.1.4

- 新特性：增加超时关闭猫猫功能

### 0.0.1.5b1

- 新特性：新增方法 base_send_group，base_send_private，base_send_group_many，
add_private_redirect，remove_private_redirect

## 0.0.2.0

重构代码

- 新特性：新增sub_state，从而实现对群成员状态的控制
- 新特性：新增AyakaSession
- 新特性：取消同一时间同一群聊只能运行一个猫猫的限制
- 破坏性变更：删除CannotFindModuleError类
- 破坏性变更：移除了remove_listener，add_listener，base_send，base_send_many，
base_send_group，base_send_private，base_send_group_many
- 破坏性变更：删除了AyakaChannel类，AyakaEvent结构变化，所有适配器已更新
- 破坏性变更：GroupMember更名为GroupMemberInfo
- 破坏性变更：cat.channel被移除
- 破坏性变更：cat.channel_types被更换为group、private参数
- 破坏性变更：AyakaParams被AyakaContext取代
- 修复BUG：多prefix时，文字回调的触发日志错误的多次打印
