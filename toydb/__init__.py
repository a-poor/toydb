"""
"""

import pathlib as _pathlib
import shutil as _shutil

from . import dtypes
from . import exceptions
from .Database import Database
from .RowStruct import RowStruct

__version__ = "0.1.0"

def create_db(dbname="database.tdb",path="."):
    """Create a new database"""
    return Database(dbname,path)

def delete_db(db: Database):
    """Delete a database"""
    db.remove()
