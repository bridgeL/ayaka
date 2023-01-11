'''cat bot.py'''
import ayaka.adapters as cat

cat.init()
cat.regist()

# 加载插件
import ayaka_games

if __name__ == "__main__":
    cat.run()
