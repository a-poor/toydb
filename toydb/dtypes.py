
class dtype:
    value = None

    def __init__(self,value,default=None):
        self.value = value
        self.default = None

    def __str__(self):
        return str(self.value)

    def __call__(self,n=1):
        return f"{n}{self.value}"

    def __getitem__(self,n=1):
        return f"{n}{self.value}"

I32 = dtype("i",0)
I64 = dtype("l",0)
F32 = dtype("f",0)
F64 = dtype("d",0)
BOOL = dtype("?",False)
CHAR = dtype("c","")
STRING = dtype("s","")
