## 0.0.0.1

喵，从[nonebot_plugin_ayaka](https://github.com/bridgeL/nonebot-plugin-ayaka)发源

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
- 新增文档站

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

重构代码，引入了sub_state的概念

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

### 0.0.2.1

- 变更：不再使用command_sep配置

### 0.0.2.2a0

- 破坏性变更：删除了bridge.get_separates方法

## 0.0.3.0

重构代码，更加规范的、更利于拓展的适配器逻辑

- 新特性：ayaka能够同时注册多个适配器
- 新特性：新增配置项 auto_detect，auto_ob11_qqguild_patch
- 新特性：新增适配器 qqguild
- 破坏性变更：删除了bridge
- 修复BUG：当命令前缀不为空时，上下文结果与预期不符，受影响的上下文：cat.arg、cat.args、cat.nums
- 优化日志表现

### 0.0.3.1

- 新特性：更好的猫猫帮助和猫猫状态，已支持sub_state
- 修复BUG：频道消息事件意外地被ob11适配器处理

### 0.0.3.2

- 新特性：新增上下文db_session
- 新特性：新增AyakaSubscribe，AyakaSubscribe可以监视某个类的属性变化，并触发相应回调，帮助开发成就系统
- 修复BUG：注册回调时，always参数没有正确生效

## 0.0.4.0

- 破坏性变更：根数据库地址变更为 data/ayaka/data.db
- 破坏性变更：ayaka不再导出get_session, UserDBBase, GroupDBBase，请使用cat.db.UserDBBase，cat.Config
- 变更：移除root_config中的block，新增CatBlock
- 新特性：新增AyakaDB，通过它，你可以让各个插件拥有独立的数据库
- 新特性：Timer可自定义formater
- 优化console使用，现在初始默认角色为群号100中uid为1的群成员

### 0.0.4.1

- 优化代码结构
- 新增配置项 prefixes，separate，ws_reverse
- 新特性：adapter.on_startup现在可以添加同步函数，请注意，所有程序都将等待其完成
- 新特性：AyakaEvent新增字段raw_messsage
- 新特性：新增适配器 gocq
- 新特性：console适配器新增指令 t
- 优化了cat.valid的实现方式，避免其使用过多的database.session

### 0.0.4.2

- 破坏性变更：移除了ayaka.core，其内部模块上升为ayaka的子模块
- 变更：cat.on_cmd取消cmds参数的缺省值
- 变更：console、gocq适配器的run方法，新增自定义参数
- 变更：trigger删除cat属性，新增cat_name属性
- 变更：初始化Cat时的提示日志从trace等级变更为debug等级
- 移除：移除了猫猫管理器的部分命令：强制休息、猫猫状态
- 新特性：适配器增加on_shutdown钩子
- 新特性：pip安装时，新增optional选项`nb2ob11`
- 新特性：ayaka_context新增prefix属性，cat属性
- 新特性：AyakaSession新增wait_next_msg方法
- 新特性：新增playwright模块
- 优化猫猫帮助表现
- 优化代码结构

### 0.0.4.3

- 变更：抽离部分数据库逻辑到外部包ayaka_db中
- 变更：AyakaSubscribe被抽离至外部包ayaka_utils中
- 新特性：session.wait_next_msg方法新增超时参数
- 新特性：playwright模块增加get_new_page方法
- 新特性：新增上下文 adapter
- 优化代码结构

### 0.0.4.4

- 变更：删除方法get_first_adapter，auto_load_adapter
- 修复BUG：特定的adapter访问顺序可能导致ayaka_context.adapter无法正常使用
- 优化ayaka_context结构

### 0.0.4.5

- 修复BUG：adapter.on_startup、adapter.on_shutdown不返回原函数

### 0.0.4.6

- 修复BUG：在hoshino框架下，raw_message解析发生报错

### 0.0.4.7

- 优化依赖：fastapi和uvicorn变为可选依赖
