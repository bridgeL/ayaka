## 直接读写（不推荐）

```py
@cat.on_cmd(cmds="test")
async def _():
    cat.cache["test"] = cat.arg

@cat.on_cmd(cmds="show")
async def _():
    arg = cat.cache.get("test", "默认值")
    await cat.send(arg)
```

缺乏类型提示，而且当需要缓存的参数过多时，代码体验尤其地狱

## get_data（推荐）

```py
from pydantic import BaseModel

class Model(BaseModel):
    test:str = "默认值"

@cat.on_cmd(cmds="test")
async def _():
    model = cat.get_data(Model)
    model.test = cat.arg

@cat.on_cmd(cmds="show")
async def _():
    model = cat.get_data(Model)
    await cat.send(model.test)
```

其保存位置 `model <-> cat.cache["Model"]`，可以使用`print(cat.cache)`来验证

使用`get_data`时，若`cat.cache["Model"]`不存在，则自动通过`Model()`初始化并存入cache（保证一定有返回值）

## pop_data

从`cat.cache`中释放指定数据

```py
from pydantic import BaseModel

class Model(BaseModel):
    test:str = "默认值"

@cat.on_cmd(cmds="test")
async def _():
    model = cat.get_data(Model)
    model.test = cat.arg

@cat.on_cmd(cmds="pop")
async def _():
    model = cat.pop_data(Model)
    await cat.send(model.test)
```

使用`pop_data`时，若`cat.cache["Model"]`不存在，则自动通过`Model()`初始化但不存入cache（保证一定有返回值）

## bot重启后数据丢失

咱只是缓存喵

## 下一步

<div align="right">
    在这里~ ↘
</div>
