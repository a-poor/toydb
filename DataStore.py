
import struct
from collections import namedtuple
from array import array

class DataStore:
    def __init__(self,schema={}):
        self.schema = schema
        self.colnames, self.types = zip(*schema.items())
        
    def pack(self,fn,data):
        
        

