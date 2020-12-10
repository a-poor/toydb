"""
"""

import json
from pathlib import Path
from datetime import datetime as dt

from .dtypes import dtypes
from .RowStruct import RowStruct

from typing import Union, Dict


class Database:
    """
    """

    # @staticmethod
    # def _validateDirectory(directory: Union[str,Path]):
    #     directory = Path(directory)

    @classmethod
    def new(cls,name="db.tdb"):
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

    def __init__(self,filename="db.tdb"):
        self.filename = Path(filename)
        self.metadata = self._loadMetadata()
        self.name = metadata.get("name")
        self._structs = self._loadStructs()

    def listTables(self):
        return list(self.metadata["tables"].keys())

    def getTableSchema(self,table_name):
        assert table_name in self.listTables()
        return self.metadata["tables"][table_name]["schema"]

    def createTable(self,table_name: str, schema: dict):
        assert table_name in self.listTables()
        self.metadata["tables"][table_name] = {
            "schema": schema,
            "indexes": []
        }
        self._writeMetadata()

    def _loadMetadata(self):
        mdf = self.filename / "metadata.json"
        return json.reads(mdf.read_text())

    def _writeMetadata(self):
        with (self.filename / "metadata.json").open("w") as f:
            json.dump(self.metadata,f)

    def _loadStructs(self):
        return {tn: RowStruct(list(d["schema"].values())) for
            tn, schema in self.metadata["tables"].items()}

    # def _validateData(self,table_name,)
