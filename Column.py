
import bisect
from array import array
from bitarray import bitarray


class Column:
    
    VALID_TYPES = (
        #  "bool",
        "int",
        "float",
        "text"
    )

    def __init__(self,name="",data=[],type="int",index=None):
        self.name = name
        self.data = data
        self.type = data.typecode
        
        assert not index or index in ('range','hash')
        self.has_idx = index is not None
        self.idx_type = index
        if self.has_idx:
            self.index = self.createIndex(index)
        else:
            self.index = None
        self.sorted = self.has_idx
        
    def createIndex(self,type_):
        pass
        
    def arrFromData(self,data,type_):
        return
        
    #### Magic Functions ####
    def __repr__(self):
        return f"<Column name={self.name} type={self.type}>"
        
    def __len__(self):
        return
        
    def __getitem__(self,i):
        return self.data[i]
        
    def __setitem__(self,i,value):
        self.data[i] = value
        
    def __contains__(self,item):
        return

    #### Setup Functions ####        
    def search(self,item):
        pass
        
    def _search_sorted(self,item):
        pass
        
    def insert(self,item):
        pass
    
    def _insert_sorted(self,item):
        pass
        
    def _insert_unsorted(self,item):
        pass
        
    def remove(self,i):
        pass
    
    
    
    
        
