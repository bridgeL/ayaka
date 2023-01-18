## 一览表

| 属性    | 意义                               | 备注                                                              | 读写性 |
| ------- | ---------------------------------- | ----------------------------------------------------------------- | ------ |
| state   | 猫猫状态                           | -                                                                 | rw     |
| cache   | 猫猫缓存                           | -                                                                 | rw     |
| help    | 猫猫帮助                           | -                                                                 | rw     |
| valid   | 当前猫猫是否可用                   | 通过猫猫管理器控制各个群组中各个猫猫的启用与禁用                  | rw     |
| event   | 当前事件                           | event.sender, event.channel, event.message, event.at, event.reply | r      |
| channel | 当前会话                           | channel.id, channel.type                                          | r      |
| user    | 当前用户                           | user.id, user.name                                                | r      |
| message | 当前消息                           | -                                                                 | r      |
| trigger | 当前触发器                         | -                                                                 | r      |
| cmd     | 当前触发命令                       | -                                                                 | r      |
| arg     | 当前消息移除命令后的内容           | -                                                                 | r      |
| args    | 当前消息移除命令后的内容进一步分割 | -                                                                 | r      |
| nums    | 当前消息中的的整数数字             | -                                                                 | r      |

## 下一步

<div align="right">
    在这里~ ↘
</div>
