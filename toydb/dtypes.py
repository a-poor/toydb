
import re
import json

from typing import Union, Any, Optional

class DType:
    def __init__(self, name: str, value: str, default: Any = None,
        has_numeric_value: bool = False):
        """A datatype for ToyDB.

        :param name: Name of the datatype
        :param value: Format string corresponding to python's struct
            `format characters <https://docs.python.org/3/library/struct.html#format-characters>`_.
        :param default: Default value of the datatype
        :param has_numeric_value: Is there a number in the ``value``
            parameter (especially useful with strings).
        """
        self.name = name
        self.value = value
        self.default = default
        self.has_numeric_value = has_numeric_value

    def __repr__(self):
        return f"<dtype: {self.name}>"

    def __str__(self):
        return str(self.value)

    def __call__(self, n: Optional[int] = None) -> str:
        """Get ``DType``'s format string with optional
        repeat number prepended.

        :param n: Prefix int prepended to ``self.value``.
            With strings, it represents the max length of
            the string. If ``n`` is ``None``, just the
            value is returned. If ``DType`` already has
            a number in its ``self.value`` string, ``n``
            must be set to ``None``.
        :return: ``struct.Struct`` format string for ``DType``.
        """
        if n is None: n = ""
        else:
            assert n > 0
            assert not self.has_numeric_value
            n = str(n)
        return f"{n}{self.value}"

    def __getitem__(self, n: int) -> "DType":
        """Another way of calling self.subtype()

        :param n: Prefix int prepended to ``self.value``.
        :return: Subtype ``DType`` with prepended count.
        """
        return self.subtype(n)

    def getLength(self):
        n = "".join(c for c in self.value if c.isdigit())
        if len(n) == 0: return None
        return int(n)

    def validate(self, val) -> bool:
        """Validates the input's type.

        :param val: Value being
        :returns: Is ``val`` a valid instance of this dtype?
        """
        if val is None: return True
        if not isinstance(val,type(self.default)):
            return False
        if isinstance(val,str):
            if len(val) > self.getLength():
                return False
        return True

    def subtype(self, n: int):
        """Creates a new DType with the same format character,
        but with a prefix number. Useful when creating

        :param n: Prefix number prepended to ``self.value``.
            With strings, it represents the max length of
            the string.
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

    def default(self, obj: dict):
        """Handles decoding string data types as
        ``DType`` objects.
        """
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
    """Checks that ``value``'s type matches ``dtype``.

    :param value: Value being checked
    :param dtype: DType to check against
    :return: Is ``value`` of type ``DType``?
    """
    return isinstance(value,type(dtype.default))

def get_type_from_value(value: Union[int,float,bool,str]) -> DType:
    """Guess the ``DType`` matching ``value``.

    :param value: Value to find matching dtype
    :return: DType matching ``value``
    """
    if isinstance(value,int):
        return I64
    if isinstance(value,float):
        return F64
    if isinstance(value,bool):
        return BOOL
    if isinstance(value,str):
        return STRING

def get_type_from_string(fmt_str: str) -> DType:
    """Get dtype from ``struct`` format string.

    :param fmt_str: format character with possible
        preceding count.
    :return: Matching dtype for format string
    """
    assert isinstance(fmt_str, str)
    just_char = re.sub(f"[^{valid_chars}]", "", fmt_str)
    assert len(just_char) == 1, f"just_char for '{fmt_str}' is '{just_char}'"
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
            return STRING[non_char]
