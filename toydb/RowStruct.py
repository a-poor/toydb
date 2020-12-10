
import struct
import itertools as it

from . import dtypes
from . import exceptions



from typing import Union, List, Dict, Any

class RowStruct:
    """Wraps the `struct.Struct` class.

    Handles null values and strings.
    """

    @staticmethod
    def _encode(txt: Union[str,None]) -> bytes:
        """Encode `str` as `bytes` and converts
        `None` to empty `bytes` obj."""
        if txt is None: return b""
        return txt.encode()

    @staticmethod
    def _decode(txt: bytes) -> str:
        """Strips `\x00` characters and decodes."""
        return txt.strip(b'\x00').decode()

    @staticmethod
    def _getDefault(type: Union[str,dtypes.DType]):
        if isinstance(type,dtypes.DType):
            type = str(type)
        if any(c in type for c in "ilfd"):
            return 0
        if "c" in type or "s" in type:
            return b""
        if "?" in type: return False

    def __init__(self, columns: List[str], types: List[Union[str,dtypes.DType]], endian=">"):
        assert len(types) > 0
        assert endian in "@=<>!"
        self.columns = columns
        self.types = types
        self.endian = endian
        self.format = self._makeFmt()
        self.row_struct = struct.Struct(self.format)
        self._strRows = [("s" in str(t)) for t in types]
        self._defaults = [self._getDefault(t) for t in types]

    def _makeFmt(self):
        """Creates a format string for the `struct.Struct`
        using `self.types`.

        Adds a boolean flag before each
        """
        valid_chars = "xc?hilqfds" + "0123456789"
        fmt = self.endian
        fmt += "".join(
            f"?{t}" for t in self.types
        )
        for c in fmt[1:]:
            if c not in valid_chars:
                raise exceptions.SchemaError(f"Fmt character '{c}' invalid.")
        assert len(fmt) % 2 == 1, "There should be an even number of chars +1 for `endian`-ness"
        assert len(fmt) > 1
        return fmt

    def _row_dict2list(self, row: Dict[str,Any]) -> list:
        assert all(r in self.columns for r in row.keys())
        res = {c: None for c in self.columns}
        res.update(row)
        return list(res.values())

    def pack(self, row: Union[List[Any], Dict[str, Any]]) -> bytes:
        #NOTE: Validate types here
        if isinstance(row, dict):
            row = self._row_dict2list(row)
        # Use bool flags to replace NA values
        not_na_flags = [(r is not None) for r in row]
        # Encode the strings, if necessary
        if any(self._strRows):
            row = [(self._encode(r) if is_s else r) for is_s, r
                in zip(self._strRows,row)]
        # Zip and flatten the iterables
        row = it.chain(*[
            (not_na, (val if not_na else dflt))
            for not_na, val, dflt in
            zip(not_na_flags,row,self._defaults)
        ])
        return self.row_struct.pack(*row)

    def unpack(self, data: bytes):
        b = self.row_struct.unpack(data)
        assert len(b) > 0
        assert len(b) % 2 == 0
        flags, row = b[::2], b[1::2]
        row = ((self._decode(r) if is_s else r)
            for is_s, r in zip(self._strRows,row))
        row = ((r if f else None)
            for f, r in zip(flags,row))
        return tuple(row)
