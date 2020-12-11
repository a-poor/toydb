"""
"""

import json
from pathlib import Path
from datetime import datetime as dt

from . import util
from . import dtypes
from .RowStruct import RowStruct

from typing import Union, Dict, Any, Sequence, List, Callable, Iterable


class Database:
    @staticmethod
    def _validateDirectory(directory: Union[str,Path]) -> bool:
        """

        :param directory: Location of the database directory
        :return: Is the directory valid?
        """
        directory = Path(directory)
        return True

    @classmethod
    def _new(cls, filename: str = "db.tdb"):
        """Initialize the filestructure of a new
        database.

        :param filename: filename for new database
        """
        filename = Path(filename)
        assert not filename.exists(), "`filename` already exists"
        # Make the database directory
        filename.mkdir()
        # And key child directories
        (filename / "tables").mkdir()
        (filename / "indexes").mkdir()
        metafile = filename / "metadata.json"
        metafile.touch()
        metafile.write_text(
            json.dumps({
                "db-name": filename,
                "tables": {},
                "created": dt.now().strftime("%Y-%m-%d %H:%M:%S")
        }))

    @classmethod
    def new(cls, filename: str = "db.tdb"):
        """Create a new database

        :param filename: Path to the new databasae
        :return: New Database instance
        """
        cls._new(filename)
        return cls(filename)

    def __init__(self, filename: str = "db.tdb"):
        """Creates an instance of a `toydb.Database`.

        If a database doesn't already exist, it will
        create a new one by calling ``Database.new()``.

        :param filename: Path to the database directory
        """
        self.filename = Path(filename)
        if self.filename.exists():
            self._validateDirectory(self.filename)
        else:
            self._new(filename)
        self.metadata = self._loadMetadata()
        self.name = self.metadata.get("name")
        self._structs = self._loadStructs()

    def __str__(self):
        return "<toydb.Database>"

    def listTables(self) -> List[str]:
        """Get a list of Database table names.

        :return: List of DB table names
        """
        return list(self.metadata["tables"].keys())

    def getTableSchema(self, table_name: str) -> Dict[str,dtypes.DType]:
        """Get the schema for table `table_name`.

        :param table_name: Name of existing table in DB
        :return: `dict` mapping from `str` column name to `dtype.DType`
        """
        table_name = table_name.lower()
        assert table_name in self.listTables()
        return self.metadata["tables"][table_name]["schema"]

    def createTable(self, table_name: str, schema: dict):
        """Create a new DB table.

        :param table_name:
        :param schema:
        """
        table_name = table_name.lower()
        assert " " not in table_name
        assert table_name not in self.listTables()
        filename = self.filename / "tables" / util.md5(table_name)
        filename.touch()
        self.metadata["tables"][table_name] = {
            "schema": schema,
            "indexes": [],
            "filename": str(filename)
        }
        self._writeMetadata()
        self._structs = self._loadStructs()

    def _loadMetadata(self) -> dict:
        """Read metadata from file.

        :return: Database metadata `dict`
        """
        mdf = self.filename / "metadata.json"
        assert mdf.exists(), "Metadata file doesn't exist"
        # Read the raw JSON file
        md = json.loads(mdf.read_text())
        # Convert string-dtypes to `DType` objects
        for td in md["tables"].values():
            td["schema"] = {k: dtypes.get_type_from_string(v)
                for k, v in td["schema"].items()}
        return md

    def _writeMetadata(self):
        """Save the current state of the metadata
        to the metadata json file in the datebase
        directory.
        """
        # Write out metadata using custom JSONEncoder
        with (self.filename / "metadata.json").open("w") as f:
            json.dump(self.metadata,f,cls=dtypes.JSONEncoder)

    def _loadStructs(self) -> Dict[str,dtypes.DType]:
        """Load structs from the metadata file.

        :return: Mapping from tables to `RowStruct`
        """
        return {tn: RowStruct(
            list(d["schema"].keys()),
            list(d["schema"].values()))
            for tn, d in self.metadata["tables"].items()}

    def printSchema(self, table_name: str):
        """Print a table's schema of column
        names and dtypes.

        :param table_name: Existing table in the database.
        """
        table_name = table_name.lower()
        table = self.metadata["tables"].get(table_name)
        assert table is not None, f"Table \"{table_name}\" doesn't exist."
        schema = table.get("schema")
        max_col_len = max(map(len,schema.keys()))
        col_header = f"Table: \"{table_name}\""
        print("","="*int(len(col_header)*1.5))
        print("",col_header)
        print("","="*int(len(col_header)*1.5))
        for col, dtype in schema.items():
            print(f" ... {col:{max_col_len}s} :: {dtype.name}")
        print("","="*int(len(col_header)*1.5))

    def _readLine(self, table_name: str, line_number: int = 0) -> List[Any]:
        """Seek then read a single row
        from a table in the database.

        :param table_name: Table to search
        :param line_number: Line number of row to read
        :return: Row from table as list
        """
        table_name = table_name.lower()
        assert table_name in self.metadata["tables"]
        tablefile = Path(self.metadata["tables"][table_name]["filename"])
        rstruct = self._structs.get(table_name)
        struct_size = rstruct.row_struct.size
        offset = struct_size * line_number
        if offset < 0:
            whence = 2
        with tablefile.open("rb") as f:
            f.seek(offset,whence)
            return rstruct.unpack(f.read(struct_size))

    def _iterReadBytes(self, filename: str, n: int) -> Iterable[bytes]:
        """Generator function for reading a
        binary file `n` bytes at a time.

        :param filename: Filename of binary file
        :param n: Number of bytes to read at a time
        :yields: ``n`` bytes from ``filename``
        """
        with open(filename,"rb") as f:
            while True:
                line = f.read(n)
                if not line: break
                yield line

    def _iterReadAllLines(self, table_name: str) -> Iterable[List]:
        """Generator function for iterating over
        all lines of a database table.

        :param table_name: Name of table in database
        :yields: Row of data from ``table_name``
        """
        table_name = table_name.lower()
        assert table_name in self.metadata["tables"]
        tablefile = Path(self.metadata["tables"][table_name]["filename"])
        lock = Path(str(tablefile) + ".lock")
        assert not lock.exists()
        rstruct = self._structs.get(table_name)
        row_size = rstruct.row_struct.size
        for row in self._iterReadBytes(tablefile,row_size):
            yield rstruct.unpack(row)

    def _readAllLines(self, table_name: str) -> List[List]:
        """

        :param table_name:
        :return: All of the data in ``table_name``
        """
        return [tuple(row) for row in self._iterReadAllLines(table_name)]

    def query(self, select: List[str], from_: str, where = None,
        order_by: List[str] = None, limit: int = None):
        """Query a database using SQL(-ish)
        style syntax.

        NOTE: This feature is still in development

        :param select: Columns to select
        :param from_: DB table to select from
        :param where: Conditionally filter results with a callable function
        :param order_by: Column to sort the results
        :param limit: Limit the number of results
        """
        from_ = from_.lower()
        assert from_ in self.listTables()

    def insert(self, table_name: str, row: Union[Sequence[Any], Dict[str, Any]]):
        """Add a new row of data into a table.

        :param table_name: Table in the database
        :param row: Row of data to add to table
        """
        table_name = table_name.lower()
        assert table_name in self.metadata["tables"]
        tablefile = Path(self.metadata["tables"][table_name]["filename"])
        rstruct = self._structs.get(table_name)
        data = rstruct.pack(row)
        # Simple lock placeholder
        lock = Path(str(tablefile) + ".lock")
        while lock.exists(): pass
        lock.touch()
        # Append the data
        with tablefile.open("ab") as f:
            f.write(data)
        # Release the lock
        lock.unlink()

    def insertMany(self, table_name: str,
        rows: Iterable[Union[Sequence[Any], Dict[str, Any]]]):
        """Insert multiple rows of data into a table.

        :param table_name: Name of table in database
        :param rows: Iterable of rows to add to table
        """
        for row in rows:
            self.insert(table_name,row)

    def delete(self, table_name: str, where = None):
        """

        :param table_name:
        :param where:
        """
        raise NotImplementedError
