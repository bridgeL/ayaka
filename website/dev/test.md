## 在console中离线调试插件

```py
# run.py
import ayaka.adapters.console as cat

# 加载插件
# do something

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```

## 通用命令

| 命令                            | 功能                             |
| ------------------------------- | -------------------------------- |
| g `<group_id> <user_id> <text>` | 模拟群聊消息                     |
| p `<user_id> <text> `           | 模拟私聊消息                     |
| d `<n>`                         | 延时n秒（n可以为小数）           |
| s `<name>`                      | 执行测试脚本 `script/<name>.txt` |
| h                               | 查看帮助                         |

## 脚本可执行的额外命令

| 命令          | 功能                             |
| ------------- | -------------------------------- |
| after `<cmd>` | 每一条命令执行后需额外执行的命令 |
| #             | 注释（必须放在每一行的开头）     |

## 设定默认角色

当你发出一条模拟消息后，ayaka会记录你使用的角色身份，例如（群聊100的uid为1的用户）

随后，你可以省略`g 100 1`，不必`g 100 1 命令`，而是直接发送`命令`

默认角色总是使用最近一条模拟消息的角色

若你刚刚启动程序，未发送任何消息，则初始角色为`g 100 1`

## 脚本示例

```
# script/stone.txt
# 测试赌石 √

# 设定默认角色（此句可省略，默认为g 100 1）
g 100 1 

# 接下来均以群聊100中的uid为1的角色来发言
赌石
敲
敲
hit
hit
exit
```

## 直接连接到gocq上

```py
# run2.py
import ayaka.adapters.gocq as cat

# 加载插件
# do something

if __name__ == "__main__":
    cat.run()
```

```
python run2.py
```

## 下一步

<div align="right">
    在这里~ ↘
</div>

