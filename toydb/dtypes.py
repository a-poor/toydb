
from enum import Enum

class dtypes(Enum):
    I32 = "i"
    I64 = "l"
    F32 = "f"
    F64 = "d"
    BOOL = "?"
    CHAR = "c"
    STRING = "s"  # NOTE: Should be preceded by length

    def infer_type(self,val):
        if isinstance(val,int):
            return self.I32
        if isinstance(val,float):
            return self.F64
        if isinstance(val,bool):
            return self.BOOL
        return self.STRING

    def validate(self,dtype,value):
        pass

    def get_max_string_len(self,values,mult=1):
        l = max(map(len,values))
        return l * max(1,mult)

    

