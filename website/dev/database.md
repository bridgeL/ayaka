使用[SQLModel](https://sqlmodel.tiangolo.com/)实现数据持久化，真香

## 创建表

```py
from sqlmodel import SQLModel, Field

class Money(SQLModel, table=True):
    # __tablename__可以用于自定义表名，当然你可以不写，使用类名作为默认值
    __tablename__ = "my_money"
    # 设置为主键
    group_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    # money
    money: int = 1000
```

## 增 insert

```py
from ayaka import get_session

async def _():
    # ...
    with get_session() as session:
        money = Money(group_id=100, user_id=1)
        session.add(money)
        session.commit()
    # ...
```

## 删 delete

```py
from ayaka import get_session

async def _():
    # ...
    with get_session() as session:
        money = Money(group_id=100, user_id=1)
        session.delete(money)
        session.commit()
    # ...
```

## 查 select

```py
from ayaka import get_session
from sqlmodel import select

async def _():
    # ...
    with get_session() as session:
        stmt = select(Money).filter_by(group_id=100, user_id=1)
        results = session.exec(stmt)
        money = results.one()
    # ...
```

## 改 update

```py
from ayaka import get_session
from sqlmodel import select

async def _():
    # ...
    with get_session() as session:
        stmt = select(Money).filter_by(group_id=100, user_id=1)
        results = session.exec(stmt)
        money = results.one()
        money.money += 1000
        session.commit()
    # ...
```

## 下一步

<div align="right">
    在这里~ ↘
</div>
