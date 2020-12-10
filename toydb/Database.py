"""
"""

import json
from pathlib import Path
from datetime import datetime as dt
import hashlib

from . import dtypes
from .RowStruct import RowStruct

from typing import Union, Dict, Any, Sequence, List


class Database:
    """
    """

    # @staticmethod
    # def _validateDirectory(directory: Union[str,Path]):
    #     directory = Path(directory)

    @classmethod
    def new(cls, name: str = "db.tdb"):
        filename = Path(name)
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
        return cls(filename)

    def __init__(self, filename: str = "db.tdb"):
        self.filename = Path(filename)
        self.metadata = self._loadMetadata()
        self.name = self.metadata.get("name")
        self._structs = self._loadStructs()

    def listTables(self):
        return list(self.metadata["tables"].keys())

    def getTableSchema(self, table_name: str):
        table_name = table_name.lower()
        assert table_name in self.listTables()
        return self.metadata["tables"][table_name]["schema"]

    def createTable(self, table_name: str, schema: dict):
        table_name = table_name.lower()
        assert " " not in table_name
        assert table_name not in self.listTables()
        filename = self.filename / "tables" / self._md5(table_name)
        filename.touch()
        self.metadata["tables"][table_name] = {
            "schema": schema,
            "indexes": [],
            "filename": str(filename)
        }
        self._writeMetadata()
        self._structs = self._loadStructs()

    def _md5(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def _loadMetadata(self) -> dict:
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
        # Write out metadata using custom JSONEncoder
        with (self.filename / "metadata.json").open("w") as f:
            json.dump(self.metadata,f,cls=dtypes.JSONEncoder)

    def _loadStructs(self) -> Dict[str,dtypes.DType]:
        return {tn: RowStruct(
            list(d["schema"].keys()),
            list(d["schema"].values()))
            for tn, d in self.metadata["tables"].items()}

    # def _validateData(self,table_name,)

    def printSchema(self, table_name: str):
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

    def _readLine(self, table_name: str, line: int) -> List[List]:
        table_name = table_name.lower()
        assert table_name in self.metadata["tables"]
        tablefile = Path(self.metadata["tables"][table_name]["filename"])
        rstruct = self._structs.get(table_name)
        with tablefile.open("rb") as f:
            f.write(data)

    def _iterReadBytes(self, filename: str, n: int):
        with open(filename,"rb") as f:
            while True:
                line = f.read(n)
                if not line: break
                yield line

    def _iterReadAllLines(self, table_name: str):
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
        return [tuple(row) for row in self._iterReadAllLines(table_name)]

    def query(self, SELECT: List[str], FROM: str, WHERE = None,
            ORDER_BY: List[str] = None, LIMIT: int = None):
        FROM = FROM.lower()
        assert FROM in self.listTables()

    def insert(self, table_name: str, row: Union[Sequence[Any], Dict[str, Any]]):
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
            rows: Sequence[Union[Sequence[Any], Dict[str, Any]]]):
        for row in rows:
            self.insert(table_name,row)

    def delete(self, table_name: str, where = None):
        raise NotImplementedError
