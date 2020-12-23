
import struct
import itertools as it

from . import dtypes
from . import exceptions

from typing import Union, List, Dict, Any


class RowStruct:

    @staticmethod
    def _encode(txt: Union[str,None]) -> bytes:
        """Encode `str` as `bytes` and handles ``None``
        by converting it to an empty `bytes` obj.
        (Assumes ``None``-ness has already been checked
        when writing data row.)

        :param txt: String to be encoded as bytes
        :return: Byte encoding of ``txt``
        """
        if txt is None: return b""
        return txt.encode()

    @staticmethod
    def _decode(txt: bytes) -> str:
        """Decodes bytes object as a string.

        Strips padding null (``\x00``) characters
        and decodes.

        :param txt: Bytes to be decoded
        :return: String decoded from ``txt``
        """
        return txt.strip(b'\x00').decode()

    @staticmethod
    def _getDefault(dtype: Union[str,dtypes.DType]) -> Any:
        """Get the default value for a datatype.

        Used when writing null column values.
        If a null value is being written,
        ``RowStruct`` will set the ``not_null``
        flag to ``False`` and write a default
        value.

        For example, the default values for
        numeric datatypes are ``0``, for booleans
        it's ``False``, and for strings it's
        ``""`` (an empty string).

        :param dtype: Datatype to get default value from
        :return: Default value for ``dtype``
        """
        if isinstance(dtype,dtypes.DType):
            dtype = str(dtype)
        if any(c in dtype for c in "ilfd"):
            return 0
        if "c" in dtype or "s" in dtype:
            return b""
        if "?" in dtype: return False

    def __init__(self, columns: List[str], types: List[dtypes.DType], endian: str = ">"):
        """Wraps the `struct.Struct` class and handles
        null values and strings.

        :param columns: Column names for data rows
        :param types: Column types for ``columns``
        :param endian: Endianness of the data. Options: ``"@=<>!"``. (See python's
            `struct docs <https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment>`_)
        """
        assert len(types) > 0
        assert endian in "@=<>!"
        self.columns = columns
        self.types = types
        self.endian = endian
        self.format = self._makeFmt()
        self.row_struct = struct.Struct(self.format)
        self._strRows = [("s" in str(t)) for t in types]
        self._defaults = [self._getDefault(t) for t in types]

    def _makeFmt(self) -> str:
        """Creates a format string for the `struct.Struct`
        using ``self.types``.

        Adds a boolean flag before each data type
        character to signal if the value is ``NA``.

        Also adds an endian character to the start
        of the format string.

        :return: Format string passed to ``struct.Struct``
        """
        valid_chars = "xc?hilqfds" + "0123456789"
        fmt = self.endian
        fmt += "".join(f"?{t}" for t in self.types)
        for c in fmt[1:]:
            if c not in valid_chars:
                raise exceptions.SchemaError(f"Fmt character '{c}' invalid.")
        assert len(fmt) % 2 == 1, "There should be an even number of chars +1 for `endian`-ness"
        assert len(fmt) > 1
        return fmt

    def _row_dict2list(self, row: Dict[str,Any]) -> list:
        """Convert a column-name-to-row-value dict
        to a ``None``-padded and properly ordered list.

        Used when writing data to a subset of
        columns, or if the columns are out of order
        in the ``row`` dict.

        :param row: Dict mapping from column names to
            column values. ``row`` doesn't need to
            include all of the columns in the table
            but all of ``row``'s keys need to be in
            the table. Also, ``row`` doesn't need to
            include all of the columns in table -- missing
            columns will be filled in with ``None``.

        :return: Correctly orderd list with ``row``'s values,
            ready to be written to the table.
        """
        assert all(r in self.columns for r in row.keys())
        res = {c: None for c in self.columns}
        res.update(row)
        return list(res.values())

    def pack(self, row: Union[List[Any], Dict[str, Any]]) -> bytes:
        """Encodes data from row to a byte string
        that can be written to the table file, per
        the ``RowStruct``'s format string.

        Wrapper around python's ``struct.pack``, which
        handles reordering columns (if necessary -- if
        ``row`` is a dict), as well as NA values.

        :param row: Row of data to be written to table.
        :return: Byte string encoding of ``row``.
        """
        if isinstance(row, dict):
            row = self._row_dict2list(row)
        # Validate the input row
        self._validateTypes(row)
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

    def _validateTypes(self, row: list):
        """Confirms the types in ``row`` before
        adding them to a table.

        :param row: A list of values to be added to
            a table in the database.
        :raises exceptions.SchemaError: If a value in row
            doesn't match the propper dtype.
        """
        for v, t in zip(row,self.types):
            if not t.validate(v):
                raise exceptions.SchemaError(
                    f'Row value "{v}" is not of type "{t}".')

    def unpack(self, data: bytes) -> List[Any]:
        """Decodes a byte encoding of a row of data
        from the table file.

        Wrapper around python's ``struct.unpack``, which
        handles NA values and strings (which are padded
        in the encoding process).

        :param data: byte encoding of row data
        :return: Row data in list form
        """
        b = self.row_struct.unpack(data)
        assert len(b) > 0
        assert len(b) % 2 == 0
        flags, row = b[::2], b[1::2]
        row = ((self._decode(r) if is_s else r)
            for is_s, r in zip(self._strRows,row))
        row = ((r if f else None)
            for f, r in zip(flags,row))
        return list(row)
