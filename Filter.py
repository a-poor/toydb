
from array import array

class Filter:
    def __init__(self,data):
        self.data = array('B',data)
        self.length = len(self.data)
        
    def __repr__(self):
        return f"<Filter len={self.length}>"
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self,i):
        return self.data[i]
        
    def __setitem__(self,i,val):
        self.data[i] = val
        
    def __and__(self,other):
        pass
        
    def __or__(self,other):
        pass
        
    def __xor__(self,other):
        pass
        
    def __iter__(self):
        for n in self.data:
            yield bool(n) 
        
