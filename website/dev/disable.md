有很多事ayaka做不到...

## 仅支持有限的消息段

相比各种各样的消息段（图片、语音、视频、xml...）

**ayaka更关心纯文字的交互**

只有text、reply和第一个at可以被转换为ayaka_event的内容

其他消息段都序列化为CQ码，以字符串的形式出现

**ayaka无法像nb2一样提供丰富的消息段的类型支持**

## 不关心定时器

ayaka无意关心定时发送消息等问题

## 这些牺牲带来了什么

ayaka能较为顺利地将使用ayaka的插件变为nb1、nb2、hoshino等机器人框架的**通用插件**

可以通过console离线地、全面地进行调试，无需gocq

## 下一步

<div align="right">
    在这里~ ↘
</div>
