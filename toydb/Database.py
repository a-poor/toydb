"""
"""

import json
import shutil
from pathlib import Path
from datetime import datetime as dt

from . import util
from . import dtypes
from .RowStruct import RowStruct

from typing import Union, Dict, Any, Sequence, List, Callable, Iterable


class Database:
    @staticmethod
    def _validateDirectory(db_path: Union[str,Path]):
        """Check that the directory is valid.

        :param directory: Location of the database directory
        :raises AssertionError: If the directory isn't valid
        """
        db_path = Path(db_path)
        md_file = db_path / "metadata.json"
        assert md_file.exists()
        assert bool(json.loads(md_file.read_text()))

    @classmethod
    def _new(cls, name: str = "db.tdb", path: str = "."):
        """Initialize the filestructure of a new
        database.

        :param filename: filename for new database
        """
        filename = Path(path) / name
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
                "db-name": name,
                "tables": {},
                "created": dt.now().strftime("%Y-%m-%d %H:%M:%S")
        }))

    @classmethod
    def new(cls, name: str = "db.tdb", path: str = "."):
        """Create a new database.

        :param filename: Path to the new databasae
        :return: New Database instance
        """
        cls._new(name,path)
        return cls(name,path)

    def __init__(self, name: str = "db.tdb", path: str = "."):
        """Creates an instance of a `toydb.Database`.

        If a database doesn't already exist, it will
        create a new one by calling ``Database.new()``.

        :param filename: Path to the database directory
        """
        self.filename = Path(path) / name
        if self.filename.exists():
            self._validateDirectory(self.filename)
        else:
            self._new(name,path)
        self.metadata = self._loadMetadata()
        self.name = self.metadata.get("db-name")
        self._structs = self._loadStructs()

    def __str__(self):
        return f"<toydb.Database {self.name}>"

    def __repr__(self):
        return str(self)

    def remove(self):
        """Deletes a database folder and
        all subdirectories."""
        shutil.rmtree(self.filename)

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

    def getTableColumns(self, table_name: str) -> List[str]:
        """Get a list of column names in a table.

        :param table_name: Name of existing table in DB
        """
        return list(self.getTableSchema(table_name))

    def createTable(self, table_name: str, schema: Dict[str,dtypes.DType],
        if_not_exists: bool = False):
        """Create a new DB table.

        :param table_name: Name of new table
        :param schema: A dictionary mapping from column
            names to their datatypes. Note: Text datatypes
            need their max lengths specified.
        :param if_not_exists: If ``True`` and the table
            already exists, it won't be overwritten,
            otherwise it will.
        """
        table_name = table_name.lower()
        assert " " not in table_name
        if if_not_exists and table_name in self.listTables():
            return
        filename = self.filename / "tables" / util.md5(table_name)
        filename.touch()
        self.metadata["tables"][table_name] = {
            "schema": schema,
            "indexes": [], # NOTE: Indexes not implemented
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
            json.dump(self.metadata,f,
                indent=2,cls=dtypes.JSONEncoder)

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

    def _iterReadAllDict(self, table_name: str):
        cols = list(self.metadata["tables"][table_name]["schema"].keys())
        for row in self._iterReadAllLines(table_name):
            yield dict(zip(cols,row))

    def _readAllLines(self, table_name: str) -> List[tuple]:
        """Read all lines in a database and return
        it as a list of tupples.

        :param table_name: Table in the database
        :return: All of the data in ``table_name``
        """
        return [tuple(row) for row
            in self._iterReadAllLines(table_name)]

    def query(self, from_: str, select: List[Union[str,Dict[str,Callable]]] = "*", where = None,
        limit: int = None):
        """Query a database using SQL(-ish) syntax.

        :param select: Columns to select
        :param from_: DB table to select from
        :param where: Conditionally filter results with a callable function
        :param limit: Limit the number of results
        """
        table_name = from_.lower()
        assert table_name in self.listTables()
        if select == "*":
            select = self.getTableColumns(table_name)
        itr = self._iterReadAllDict(table_name)
        if limit is not None and limit > 0:
            itr = util.iter_limit(itr,limit)
        # Create SELECT getters
        iden = lambda val: val
        if isinstance(select,str):
            select = {select:iden}
        if isinstance(select,(list,tuple)):
            select = {k: iden for k in select}
        select = {k.lower():v for k, v in select.items()}
        # SELECT and WHERE iterator
        result = (
            tuple(get(row[col]) for col, get in select.items())
            for row in itr if where is None or where(row))
        # Limit the result
        if limit is not None and limit > 0:
            return list(util.iter_limit(result,limit))
        return list(result)

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
        # Append the data
        with tablefile.open("ab") as f:
            f.write(data)

    def insertMany(self, table_name: str,
        rows: Iterable[Union[Sequence[Any], Dict[str, Any]]]):
        """Insert multiple rows of data into a table.

        :param table_name: Name of table in database
        :param rows: Iterable of rows to add to table
        """
        for row in rows:
            self.insert(table_name,row)

    def _createTempTable(self, table_name: str) -> Path:
        """Create a temporary table version of
        a database table.

        :param table_name: Table in the database
        :return: Path to the new table
        """
        assert table_name in self.metadata["tables"]
        tbl_path = Path(self.metadata["tables"][table_name]["filename"])
        tmp_table = tbl_path.with_suffix(".tmp")
        tmp_table.touch()
        return tmp_table

    def delete(self, table_name: str, where: Callable[[dict],bool]):
        """Delete rows from a table in the
        database where callable ``where``
        evaluates to true.

        Similar to the SQL ``DELETE FROM`` command.

        :param table_name: Table in the database
        :param where: Callable that gets a row from the
            table as an argument (as a dict, mapping
            from column name to value) and should return
            ``True`` if that row should be deleted and
            ``False`` otherwise.
        """
        assert table_name in self.metadata["tables"]
        tbl_path = Path(self.metadata["tables"][table_name]["filename"])
        tmp_path = self._createTempTable(table_name)
        rstruct = self._structs.get(table_name)
        for row in self._iterReadAllDict(table_name):
            if not where(row):
                self.insert(table_name,row)
        # "commit" the change
        tmp_path.rename(tbl_path)

    def dropTable(self, table_name: str):
        """Delete a table from the database.

        :param table_name: Table in database
        """
        assert table_name in self.metadata["tables"]
        table = Path(self.metadata["tables"][table_name]["filename"])
        table.unlink()
        del self.metadata["tables"][table_name]
        self._writeMetadata()
