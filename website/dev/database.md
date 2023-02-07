使用[SQLModel](https://sqlmodel.tiangolo.com/)实现数据持久化，真香

## 创建表

```py
from ayaka import AyakaCat

cat = AyakaCat("test", db="test_hhhh")

class Money(cat.db.UserDBBase, table=True):
    # __tablename__可以用于自定义表名，当然你可以不写，使用类名作为默认值
    __tablename__ = "my_money"
    # money
    money: int = 1000

# ayaka会在asgi服务启动后自动创建所有SQLModel表
```

数据库位置`data/test_hhhh/data.db`

## 增 insert

```py
@cat.on_text()
async def _():
    money = Money(group_id=100, user_id=1)
    cat.db_session.add(money)
    # cat.db_session会在回调结束后自动commit
```

## 删 delete

```py
async def _():
    money = Money(group_id=100, user_id=1)
    cat.db_session.delete(money)
    # cat.db_session会在回调结束后自动commit
```

## 查 select， 改 update

```py
from sqlmodel import select

async def _():
    # 查
    stmt = select(Money).filter_by(group_id=100, user_id=1)
    cursor = cat.db_session.exec(stmt)
    money = cursor.one()

    # 改
    money.money += 1000
    # cat.db_session会在回调结束后自动commit
```

## 下一步

<div align="right">
    在这里~ ↘
</div>
