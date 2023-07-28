"""Define global variables"""

epi_inv = 2**10

epi=1/epi_inv

complex_table = dict()

complex_entry_table = dict()

cacheCount = 1

class ComplexTableEntry:
    def __init__(self,val=0):
        self.val = val
        self.next = None
        self.ref = None
        
    def __str__(self):
        return str(val)
        
class Complex:
    def __init__(self,r_val=None,i_val=None):
        self.r = r_val
        self.i = i_val
        
    def __add__(self,other):
        res = Complex(cacheAvail,cacheAvail.next)
        res.r.val = self.r.val+other.r.val
        res.i.val = self.i.val+other.i.val
        return res
    
    def __sub__(self,other):
        res = Complex(cacheAvail,cacheAvail.next)
        res.r.val = self.r.val-other.r.val
        res.i.val = self.i.val-other.i.val
        return res    
    
    def __mul__(self,other):
        
        if self==cn0 or other == cn0:
            return cn0         
        
        res = Complex(cacheAvail,cacheAvail.next)
        if self==cn1:
            res.r.val = other.r.val
            res.i.val = other.i.val
            return res
        
        if other==cn1:
            res.r.val = self.r.val
            res.i.val = self.i.val
            return res
    
    
        ar=self.r.val
        ai=self.i.val
        br=other.r.val
        bi=other.i.val
        
        res.r.val = ar*br-ai*bi
        res.i.val = ar*bi+ai*br
        return res
    
    def __truediv__(self,other):
        
        if self==other:
            return cn1
        
        if self == cn0:
            return cn0
        
        res = Complex(cacheAvail,cacheAvail.next)
        
        if other==cn1:
            res.r.val = self.r.val
            res.i.val = self.i.val
            return res        
        
        ar=self.r.val
        ai=self.i.val
        br=other.r.val
        bi=other.i.val
        
        cmag = br*br+bi*bi
        res.r.val = (ar*br+ai*bi)/cmag
        res.i.val = (ai*br-ar*bi)/cmag
        return res   
    
    def norm(self):
        ar=self.r.val
        ai=self.i.val
        return ar*ar+ai*ai
    
    
    def __eq__(self,other):
        if self.r == other.r and self.i==other.i:
            return True
        else:
            return False
        
    def __str__(self):
        return str(self.r.val+1j*self.i.val)        
        
        
zeroEntry = ComplexTableEntry(0) 
oneEntry = ComplexTableEntry(1) 
moneEntry = ComplexTableEntry(-1) 
        
cn0 = Complex(zeroEntry,zeroEntry)
cn1 = Complex(oneEntry,zeroEntry)
# cnm1 = Complex(moneEntry,zeroEntry)

cacheAvail = ComplexTableEntry()
Avail = ComplexTableEntry()


def cn_mul(res:Complex, a:Complex, b:Complex):
    """res=a*b"""
    if equalsOne(a):
        res.r.val = b.r.val
        res.i.val = b.i.val
        return
    if equalsOne(b):
        res.r.val = a.r.val
        res.i.val = a.i.val
        return 
    if equalsZero(a) or equalsZero(b):
        res.r.val = 0
        res.i.val = 0
        return 

    ar=a.r.val
    ai=a.i.val
    br=b.r.val
    bi=b.i.val
        
    res.r.val = ar*br-ai*bi
    res.i.val = ar*bi+ai*br

def cn_mulCached(a:Complex,b:Complex):
#     res = getCachedComplex()
    global cacheAvail,cacheCount
    res = Complex(cacheAvail,cacheAvail.next)
    cacheAvail=cacheAvail.next.next
    cacheCount-=2
    if equalsOne(a):
        res.r.val = b.r.val
        res.i.val = b.i.val
        return res
    if equalsOne(b):
        res.r.val = a.r.val
        res.i.val = a.i.val
        return res
    if equalsZero(a) or equalsZero(b):
        res.r.val = 0
        res.i.val = 0
        return res
    ar=a.r.val
    ai=a.i.val
    br=b.r.val
    bi=b.i.val
    res.r.val = ar*br-ai*bi
    res.i.val = ar*bi+ai*br
    return res


def cn_div(res:Complex, a:Complex, b:Complex):
        if a == cn0:
            res.r.val = 0
            res.i.val = 0
            return 
    
        if a==b:
            res.r.val=1
            res.i.val=0
            return 
                
        if b==cn1:
            res.r.val = a.r.val
            res.i.val = a.i.val
            return       
        
        ar=a.r.val
        ai=a.i.val
        br=b.r.val
        bi=b.i.val
        
        cmag = br*br+bi*bi
        res.r.val = (ar*br+ai*bi)/cmag
        res.i.val = (ai*br-ar*bi)/cmag
        
def cn_divCached(a:Complex,b:Complex):
#     c = getCachedComplex()
    global cacheAvail,cacheCount
    c = Complex(cacheAvail,cacheAvail.next)
    cacheAvail=cacheAvail.next.next
    cacheCount-=2
    cn_div(c,a,b)
    return c    

def cn_add(res:Complex, a:Complex, b:Complex):
    """res=a*b"""
    res.r.val = a.r.val+b.r.val
    res.i.val = a.i.val+b.i.val

def cn_addCached(a:Complex,b:Complex):
#     c = getCachedComplex()
    global cacheAvail,cacheCount
    c = Complex(cacheAvail,cacheAvail.next)
    cacheAvail=cacheAvail.next.next
    cacheCount-=2
    c.r.val = a.r.val+b.r.val
    c.i.val = a.i.val+b.i.val
    return c


        
def Find_Or_Add_Complex_table(c : Complex):
#     print('fc',c)
    if c==cn0:
        return cn0
    if c==cn1:
        return cn1
    
    val_r = c.r.val
    val_i = c.i.val
    abs_r = abs(val_r)
    abs_i = abs(val_i)
    
    res = Complex()
    
    if abs_i<epi:
        if abs_r<epi:
            return cn0
        if abs(val_r-1)<epi:
            return cn1
        if abs(val_r+1)<epi:
            return Complex(moneEntry,zeroEntry)
        res.i = zeroEntry
#         key_r = int(val_r/epi)
        key_r=int(val_r*epi_inv)
        if not key_r in complex_table:
#             temp_r = getComplexTableEntry()
#             temp_r.val = val_r
            temp_r = ComplexTableEntry(val_r)
            complex_table[key_r] = temp_r
            res.r = temp_r
        else:
            res.r=complex_table[key_r]
        return res
    
    if abs_r<epi:
        if abs(val_i-1) < epi:
            return Complex(zeroEntry,oneEntry)
        if abs(val_i+1)<epi:
            return Complex(zeroEntry,moneEntry)
        res.r = zeroEntry
#         key_i = int(val_i/epi)
        key_i=int(val_i*epi_inv)
        if not key_i in complex_table:
#             temp_i = getComplexTableEntry()
#             temp_i.val = val_i
            temp_i = ComplexTableEntry(val_i)
            complex_table[key_i] = temp_i
            res.i = temp_i
        else:
            res.i=complex_table[key_i]
        return res    
    
#     key_r = int(val_r/epi)
#     key_i = int(val_i/epi)
    key_r=int(val_r*epi_inv)
    key_i=int(val_i*epi_inv)
#     print('key',key_r,key_i)
    if not key_r in complex_table:
#         temp_r = getComplexTableEntry()
#         temp_r.val = val_r
        temp_r = ComplexTableEntry(val_r)
        complex_table[key_r] = temp_r
        res.r = temp_r
    else:
        res.r=complex_table[key_r]    
    if not key_i in complex_table:
#         temp_i = getComplexTableEntry()
#         temp_i.val = val_i
        temp_i = ComplexTableEntry(val_i)
        complex_table[key_i] = temp_i
        res.i = temp_i
    else:
        res.i=complex_table[key_i]
#     print('fres',res)
    return res 

def getComplexTableEntry():
    global Avail
    c = Avail
    Avail = c.next
    return c
              
def getCachedComplex():
    global cacheAvail,cacheCount
    c = Complex(cacheAvail,cacheAvail.next)
    cacheAvail=cacheAvail.next.next
    cacheCount-=2
    return c

def getCachedComplex2(r_val,i_val):
    global cacheAvail,cacheCount
    c = Complex(cacheAvail,cacheAvail.next)
    cacheAvail=cacheAvail.next.next
    cacheCount-=2
    c.r.val = r_val
    c.i.val = i_val
    cacheCount-=1
    return c

def getTempCachedComplex():
    return Complex(cacheAvail,cacheAvail.next)

def getTempCachedComplex2(c:complex):
    res = Complex(cacheAvail,cacheAvail.next)
    res.r.val = c.real
    res.i.val = c.imag
    return res


def releaseCached(c):
    global cacheAvail,cacheCount
    c.i.next = cacheAvail
    cacheAvail=c.r
    cacheCount+=2

def equalsZero(c):
    return c==cn0 or (abs(c.r.val)<epi and abs(c.i.val)<epi)

def equalsOne(c):
    return c==cn1 or (abs(c.r.val-1)<epi and abs(c.i.val)<epi)

def equals(a:Complex,b:Complex):
    return (abs(a.r.val-b.r.val)<epi and abs(a.i.val-b.i.val)<epi)

def ini_complex(cache_size=500,table_size=10000):
    global complex_table,complex_entry_table,cacheCount,cacheAvail,Avail
    complex_table = dict()
    cacheCount = cache_size
    cache_head = cacheAvail
#     print(cacheAvail)
    for k in range(2*cache_size-1):
        temp = ComplexTableEntry()
        cache_head.next=temp
        cache_head=temp
        
#     table_head = Avail
#     for k in range(cache_size-1):
#         temp = ComplexTableEntry()
#         table_head.next=temp
#         table_head=temp
    
