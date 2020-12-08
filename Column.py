
class Column:

    def __init__(self,name,data,type,indexed=False):
        self.name = name
        self.data = data
        self.type = type
        self.indexed = indexed
    
    def __repr__(self):
        return f"<Column name=\"{self.name}\" type=\"{self.type}\">"
        
    def __getitem__(self,i):
        iterables = (list,tuple)
        if any(map(lambda t: isinstance(i,t),iterables)):
            return [self[ii] for ii in i]
        return self.data[i]
        
    def __setitem__(self,i,val):
        self.data[i] = val
        
    def _makeIndex(self):
        pass
        
        
