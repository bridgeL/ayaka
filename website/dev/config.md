使用[pydantic](https://docs.pydantic.dev/)的`BaseModel`，真香

## 作为配置使用

### 定义

```py
from ayaka import AyakaConfig
# AyakaConfig 是 BaseModel 的子类

class Config(AyakaConfig):
    __config_dir__ = "testttt"
    __config_name__ = "我是配置"
    version:str = "1.0.0"
    greeting:str = "你好"
    reward:int = 20
    names:list[str] = []
```

你也可以这样定义

```py
cat = AyakaCat("testttt")

class Config(cat.Config):
    __config_name__ = "我是配置"
    version:str = "1.0.0"
    greeting:str = "你好"
    reward:int = 20
    names:list[str] = []

```

### 加载与读取

```py
# 从本地加载
config = Config()

# 读取
# do something
config.reward
```

配置将保存在`data/testttt/我是配置.json`中

### 写入

配置文件可以在代码中动态修改，而非仅外部可修改

**对于不可变对象**

直接赋值，`AyakaConfig`会**自动**将新值写入本地配置文件中

```py
config.reward = 10000
```

**对于可变对象**

需要**手动**执行`config.save`方法，将新值写入本地配置文件中

```py
config.names.append("oh no")
config.save()
```

## 作为持久化数据的手段

缓存数据在bot重启后会丢失，可以使用`AyakaConfig`来保存需要持久化的数据

不过，这可能会导致一些概念上的混乱，配置与数据混杂在一起并不是什么好事

当然对于数据量较小且多变的情况而言，使用`AyakaConfig`也是一种不错的选择

## 下一步

<div align="right">
    在这里~ ↘
</div>
