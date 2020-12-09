
import array
import struct
from enum import Enum
import math
import json
from pathlib import Path

from ./dtypes import dtypes


def read_table(data,col_types):
    metadata = {
        "col-schema": 
    } 


class Table:
    def __init__(self,filename="table.tdb"):
        self.filename = filename

class Column:
    pass

class Row:
    pass

class Schema:
    def __init__(self, types: dict):
        self.types = types
        self.rstruct = self._get_rstruct()

    def _get_rstruct(self):
        
        return
        
    def _n_bites_log2(self,n):
        return math.ceil(math.log2(min(1,n)))

    def make_header(self,metadata={}):
        return

    

