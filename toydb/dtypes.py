
import re
import json

from typing import Union

class DType:
    def __init__(self, name: str, value, default=None, has_numeric_value=False):
        """
        """
        self.name = name
        self.value = value
        self.default = None
        self.has_numeric_value = has_numeric_value

    def __repr__(self):
        return f"<dtype: {self.name}>"

    def __str__(self):
        return str(self.value)

    def __call__(self, n: int=None):
        """
        """
        if n is None: n = ""
        else:
            assert n > 0
            assert not self.has_numeric_value
            n = str(n)
        return f"{n}{self.value}"

    def subtype(self, n: int):
        """
        """
        return self.__class__(
            f"{self.name}[{n}]",
            f"{n}{self.value}",
            self.default,
            True)

class JSONEncoder(json.JSONEncoder):
    """Subclass of `json.JSONEncoder` that is able
    to encode `dtype.DType` when calling `json.dump()`.
    """
    def default(self,obj):
        if isinstance(obj,DType):
            return obj.value
        else:
            return super().default(obj)


I32 = DType("Int32","i",0)
I64 = DType("Int64","l",0)
F32 = DType("Float32","f",0)
F64 = DType("Float64","d",0)
BOOL = DType("Bool","?",False)
CHAR = DType("Char","c","")
STRING = DType("String","s","")
STRING50 = STRING.subtype(50)

valid_chars = "ilfd?cs"
supported_types = [
    I32,
    I64,
    F32,
    F64,
    BOOL,
    CHAR,
    STRING,
    STRING50,
]

def validate(value: Union[int,float,bool,str], dtype: DType) -> bool:
    """

    :param value:
    :param dtype:
    :return:
    """
    return isinstance(value,type(dtype.default))

def get_type_from_value(value: Union[int,float,bool,str]) -> DType:
    """

    :param value:
    :return:
    """
    if isinstance(value,int):
        return I32
    if isinstance(value,float):
        return F64
    if isinstance(value,bool):
        return BOOL
    if isinstance(value,str):
        return STRING

def get_type_from_string(fmt_str: str) -> DType:
    """

    :param fmt_str:
    :return:
    """
    assert isinstance(fmt_str, str)
    just_char = re.sub(r"[^a-z]", "", fmt_str)
    assert len(just_char) == 1
    if len(just_char) == len(fmt_str):
        non_char = None
    else:
        non_char = int(re.sub(r"[a-z]", "", fmt_str))
        assert non_char > 0
    if just_char == I32.value: return I32
    if just_char == I64.value: return I64
    if just_char == F32.value: return F32
    if just_char == F64.value: return F64
    if just_char == BOOL.value: return BOOL
    if just_char == CHAR.value: return CHAR

    if just_char == "s":
        if non_char is None:
            return STRING
        else:
            return STRING.subtype(non_char)
