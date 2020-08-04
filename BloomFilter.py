
import math
import random
import mmh3
from bitarray import bitarray

class BloomFilter:
    
    @staticmethod
    def probFalsePos(m,k,n):
        """
        Args:
            m -> size of bit array
            n -> number of expected elements
            k -> number of hash functions
        Returns:
            p -> prob of getting a false positive
        """
        return (1-(1-(1/m))**(k*n))**k
        
    @staticmethod
    def bitArrSize(n,p):
        """
        Args:
            n -> expected number of elements
            p -> desired false positive prob
        Returns:
            m -> size of bit array
        """
        return max(1,int(-(n * math.log(p)) / (math.log(2)**2)))
        
    @staticmethod
    def nHashFns(m,n):
        """
        Args:
            m -> size of bit array
            n -> n elements to insert
        Returns:
            k -> optimum num hash functions
        """
        k = m * math.log(2) / n
        return max(1,int(k))
        
    
    def __init__(self,nexpected=1_000,probfp=0.05):
        self.probfp = probfp
        self.size = BloomFilter.bitArrSize(nexpected,probfp)
        self.hashcount = BloomFilter.nHashFns(self.size,nexpected)
        self.bitarr = bitarray(self.size)
        self.bitarr.setall(0)
        self.nadded = 0
        
    def __len__(self):
        return self.nadded
        
    def __repr__(self):
        return f"<BloomFilter size: {self.size} n-items: {self.nadded}>"
        
    def __contains__(self,item):
        return self.check(item)
        
    def add(self,item):
        for i in range(self.hashcount):
            digest = mmh3.hash(item,i) % self.size
            self.bitarr[digest] = True
        self.nadded += 1
        
    def check(self,item):
        for i in range(self.hashcount):
            digest = mmh3.hash(item,i) % self.size
            if not self.bitarr[digest]:
                return False
        return True
        
    def clear(self):
        self.bitarr.setall(0)
        self.nadded = 0
    

        
    
