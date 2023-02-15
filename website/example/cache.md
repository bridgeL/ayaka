注意：缓存数据会在bot重启后丢失

## 数据缓存

ayaka为每个群聊均设置了一份字典

各个插件中的猫猫均可以通过`cat.cache`访问到该字典中的一部分空间

各个群聊所对应的cache是不同的，互不干涉

## 类型提示

同时，ayaka还设计了`cat.get_data`、`cat.pop_data`方法读写`cat.cache`

可以将`BaseModel`放入其中使用，解决了直接读写字典时缺乏类型提示的问题

## 子数据缓存

与state时面临的情况一致，有时候我们希望同一个群、不同群成员所访问到的缓存空间也各不相同、互不干涉

那么你需要使用`cat.user.cache`

同样，你也可以使用`cat.user.get_data`和`cat.user.pop_data`方法读写`cat.user.cache`

## 下一步

<div align="right">
    在这里~ ↘
</div>
