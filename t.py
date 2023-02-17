dd = []

class Test:
    def __new__(cls, name):
        if cls not in dd:
            dd.append(cls)
        return cls
    
    def __init__(self, name) -> None:
        self.name = name

class Tddd(Test):
    ...

print(dd)    
a = Test(1)
b = Tddd(2)
print(dd)    
print(id(a) == id(b))