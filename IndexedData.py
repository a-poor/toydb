
import bisect
from array import array

class IndexedData:
    
    def __init__(self,data,type=""):
        self.type = type
        self.data = array(type)
        self.index = array("I")
        for i, n in enumerate(data):
            pos = bisect.bisect(self.data,n)
            self.data.insert(pos,n)
            self.index.insert(pos,i)
        
    def __repr__(self):
        return self.data
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self,i):
        return 
        
    def add(self,value):
        pass
        

