import numpy as np
import copy
import time
"""Define global variables"""
computed_table = dict()
global_unique_table = dict()
global_index_order = dict()
global_node_idx=0

class Index:
    """The index, here idx is used when there is a hyperedge"""
    def __init__(self,key,idx=0):
        self.key = key
        self.idx = idx
        
    def __eq__(self,other):
        if self.key == other.key and self.idx == other.idx:
            return True
        else:
            return False
    def __lt__(self,other):
        self_order = global_index_order.index(self.key)
        other_order = global_index_order.index(other.key)
        return self_order < other_order
    def __str__(self):
        return str((self.key,self.idx))
    
class Node:
    """To define the node of TDD"""
    def __init__(self,key):
        self.idx = 0 #the unique identification
        self.key = key #the index of the node
        self.level=0
        self.out_weight=[1]*2
        self.successor_level=0
        self.successor=[None]*2
        self.ref_cont=0
        self.is_normalized=True
        self.weight=1

class TDD:
    def __init__(self,node):
        """TDD"""
        self.weight=1
        
        self.index_set=[]
        
        self.unique_table=dict()
        
        if isinstance(node,Node):
            self.node=node
        else:
            self.node=Node(node)
            
    def node_number(self):
        node_set=set()
        node_set=get_node_set(self.node,node_set)
        return len(node_set)
    
    def self_copy(self):
        temp = TDD(self.node)
        temp.weight = self.weight
        temp.index_set = self.index_set
        temp.unique_table=self.unique_table
        return temp
    
    def __eq__(self,other):
        if self.node==other.node and get_int_key(self.weight)==get_int_key(other.weight):
            return True
        else:
            return False

    def contract(self,other):
        #this is a non-normalised contract, usually used when self is big anf the other is small
        var_out,var_cont=get_contract_index(self,other)
        res=loc_contract(self,other,var_cont)
        self.node=res.node
        self.weight=res.weight
        self.index_set=var_out
        self.unique_table=res.unique_table
        
        
def Ini_TDD(var_order=[]):
    """To initialize the unique_table,computed_table and set up a global index order"""
    global computed_table
    global global_unique_table
    global global_index_order
    global global_node_idx
    
    global_node_idx=0
    global_unique_table = dict()
    computed_table = dict()
    global_index_order = copy.copy(var_order)
    global_index_order.append(1)
    node = Find_Or_Add_Unique_table(1,0,0,None,None)
    tdd = TDD(node)
    return tdd    

def get_unique_table():
    return global_unique_table

def get_unique_table_num():
    return len(global_unique_table)


def set_index_order(var_order):
    global global_index_order
    global_index_order = copy.copy(var_order)
    global_index_order[1] = float('inf')
    
def get_index_order():
    global global_index_order
    return copy.copy(global_index_order)
    
def get_int_key(weight):
    """To transform a complex number to a tuple with int values"""
    epi=0.000001     
    return (int(round(weight.real/epi)) ,int(round(weight.imag/epi)))

def get_node_set(node,node_set=set()):
    """Only been used when counting the node number of a TDD"""
    if not node in node_set:
        node_set.add(node)
        for k in range(2):
            if node.successor[k]:
                node_set = get_node_set(node.successor[k],node_set)
    return node_set

def Find_Or_Add_Unique_table(x,weight1,weight2,node1,node2,unique_table=None):
    """To return a node if it already exist, creates a new node otherwise"""
    global global_node_idx
    if unique_table==None:
        global global_unique_table
        unique_table=global_unique_table
    if not isinstance(x,str):
        if unique_table.__contains__(x):
            return unique_table[x]
        else:
            res=Node(x)
            res.idx=0
            unique_table[x]=res
        return res
#     if not x in unique_table:
#         unique_table[x]=dict()
    temp_key=(x,get_int_key(weight1),get_int_key(weight2),node1.idx,node2.idx)
    if temp_key in unique_table:
        return unique_table[temp_key]
    else:
        res=Node(x)
        global_node_idx+=1
        res.idx=global_node_idx
        res.out_weight=[weight1,weight2]
        res.successor=[node1,node2]
        unique_table[temp_key]=res
        print(temp_key,res.idx)
    return res

def normalize(x,low,high,unique_table=None):
    """The normalize and reduce procedure"""
    if high==low:
        return high
    weig1=low.weight
    weig2=high.weight
    epi=0.000001

    if get_int_key(weig1)==(0,0) and get_int_key(weig2)==(0,0):
        node=Find_Or_Add_Unique_table(1,0,0,None,None)
        res=TDD(node)
        res.weight=0
        return res
    elif get_int_key(weig1)==(0,0):
        node=Find_Or_Add_Unique_table(1,0,0,None,None)
        low=TDD(node)
        weig1=0
    elif get_int_key(weig2)==(0,0):
        node=Find_Or_Add_Unique_table(1,0,0,None,None)
        high=TDD(node)
        weig2=0
        
    if np.around(abs(weig1)/epi)>=np.around(abs(weig2)/epi):
        weig=weig1
    else:
        weig=weig2

    weig1=weig1/weig
    weig2=weig2/weig
    node=Find_Or_Add_Unique_table(x,weig1,weig2,low.node,high.node,unique_table)
    res=TDD(node)
    res.weight=weig
    return res


def global_normalize(tdd,unique_table=None):
    term=Find_Or_Add_Unique_table(1,0,0,None,None)
    if tdd.node.key==1:
        res=TDD(term)
        res.weight=tdd.weight*tdd.node.weight
        return res
    else:
        x=tdd.node.key
        level=tdd.node.successor_level
        
        if unique_table==None:
            unique_table=dict()
            
        if not tdd.node.successor[0].idx in tdd.unique_table[level]:
            low=TDD(term)
            low.weight=tdd.node.out_weight[0]
        else:
            node=tdd.unique_table[level][tdd.node.successor[0].idx]
            low=TDD(node)
            low.unique_table=tdd.unique_table
            low=global_normalize(low,unique_table)
            low.weight=low.weight*node.weight*tdd.node.out_weight[0]
        if not tdd.node.successor[1].idx in tdd.unique_table[level]:
            high=TDD(term)
            high.weight=tdd.node.out_weight[1]
        else:
            node=tdd.unique_table[level][tdd.node.successor[1].idx]                        
            high=TDD(node)
            high.unique_table=tdd.unique_table
            high=global_normalize(high,unique_table)
            high.weight=high.weight*node.weight*tdd.node.out_weight[1]       
        res=normalize(x,low,high)
        res.weight*=tdd.weight
        res.node.level=global_index_order.index(x)
        res.node.successor_level=low.node.level
        res.index_set = copy.copy(tdd.index_set)
        if not res.node.level in unique_table:
            unique_table[res.node.level]=dict()
        if not res.node.idx in unique_table[res.node.level]:
            unique_table[res.node.level][res.node.idx]=res.node      
        res.unique_table=unique_table
        return res
        
        
def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table
    the_keys = []
    if item[0]=='s':
        the_keys.append(('s',get_int_key(item[1].weight),item[1].node,item[2],item[3]))
    elif item[0] == '+':
        the_keys.append(('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node))
        the_keys.append(('+',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node))
    else:
        the_keys.append(('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3]))
        the_keys.append(('*',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node,item[3]))
    for the_key in the_keys:
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
    return None

def insert_2_computed_table(item,res):
    """To insert an item to the computed table"""
    global computed_table
    if item[0]=='s':
        the_key = ('s',get_int_key(item[1].weight),item[1].node,item[2],item[3])
    elif item[0] == '+':
        the_key = ('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
    else:
        the_key = ('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3])
    computed_table[the_key] = (res.weight,res.node)
    

    
def get_tdd(U,var,unique_table=None):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    if sum(U.shape)==U_dim:
        node=Find_Or_Add_Unique_table(1,0,0,None,None)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
        return res
    if unique_table==None:
        unique_table=dict()
    min_index=min(var)
    x=min_index.key
    min_pos=var.index(min_index)
    new_var=copy.copy(var)
    new_var[min_pos]=Index(1)
    split_U=np.split(U,2,min_pos)
    low=get_tdd(split_U[0],new_var,unique_table)
    high=get_tdd(split_U[1],new_var,unique_table)
    tdd = normalize(x, low, high)
    tdd.node.level=global_index_order.index(x)
    tdd.node.successor_level=low.node.level
    tdd.var_set = copy.copy(var)
    if not tdd.node.level in unique_table:
        unique_table[tdd.node.level]=dict()
    if not tdd.node.idx in unique_table[tdd.node.level]:
        unique_table[tdd.node.level][tdd.node.idx]=tdd.node      
    tdd.unique_table=unique_table
    return tdd
    
    
# def tensor_product(): 

    
def get_contract_index(tdd1,tdd2):    
    var_out=[]
    var_cont=[]
    for var in tdd1.index_set:
        if var in tdd2.index_set:
            if not var.key in var_conted:
                var_cont.append(var.key)
        else:
            var_out.append(var)
    for var in tdd2.index_set:
        if not var in tdd1.index_set:
            var_out.append(var)
    var_out_key=[]
    for var in var_out:
        var_out_key.append(var.key)
        
    var_temp=[]
    for var in var_cont:
        if not var in var_out_key:
            var_temp.append((global_index_order.index(var),var))
    var_temp.sort()
    var_cont=[]
    
    for item in var_temp:
        var_cont.append(item[1])
    
    return var_out,var_cont
    
def loc_contract(tdd1,tdd2,var_cont):
    """To local contract tdd1 and tdd2"""
    global global_index_order
    
    v1=tdd1.node.key
    v2=tdd2.node.key
    
    term=Find_Or_Add_Unique_table(1,0,0,None,None)

    if v1==1 and v2==1:
        weig=(2**len(var_cont))*tdd1.weight*tdd2.weight
        tdd=TDD(term)
        if get_int_key(weig)==(0,0):
            tdd.weight=0
        else:
            tdd.weight=weig
        return tdd

    if v1==1:
        if len(var_cont)==0:
            weig=tdd1.weight*tdd2.weight
            if get_int_key(weig)==(0,0):
                tdd=TDD(term)
                tdd.weight=0
            else:
                node=tdd2.node
                tdd=TDD(node)
                tdd.weight=weig
            tdd.unique_table=tdd2.unique_table
            return tdd          
            
    if v2==1:
        return loc_contract(tdd2,tdd1,var_cont)
    
    w1=tdd1.weight
    w2=tdd2.weight
    tdd1.weight=1
    tdd2.weight=1
    
    if find_computed_table(['*',tdd1,tdd2,tuple(var_cont)]):
        tdd = find_computed_table(['*',tdd1,tdd2,tuple(var_cont)])
        tdd.weight=tdd.weight*w1*w2
        return tdd
    if global_index_order.index(v1)<=global_index_order.index(v2):
        x=v1
    else:
        x=v2
        
    if len(var_cont)==0:
        low=contract(Slicing(tdd1,x,0),Slicing(tdd2,x,0),var_cont)
        high=contract(Slicing(tdd1,x,1),Slicing(tdd2,x,1),var_cont)
        tdd=normalize(x,low,high)
        insert_2_computed_table(['*',tdd1,tdd2,tuple(var_cont)],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    elif x == var_cont[0]:
        new_var_cont=copy.copy(var_cont)
        new_var_cont.remove(x)
        low=contract(Slicing(tdd1,x,0),Slicing(tdd2,x,0),new_var_cont)
        high=contract(Slicing(tdd1,x,1),Slicing(tdd2,x,1),new_var_cont)
        tdd=add(low,high)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    else:
        x = var_cont[0]
        cont_level=global_index_order.index(x)
        for key1 in tdd1.unique_table[cont_level]:
            temp_node1=tdd1.unique_table[cont_level][key1]
#             for key2 in tdd2.unique_table[cont_level]:
#                 temp_node2=tdd2.unique_table[cont_level][key2]
            if x == v2:
                temp_tdd2=tdd2
            else:
                temp_tdd2=normalize(x,Slicing(tdd2,x,0),Slicing(tdd2,x,1))
            temp_tdd1 = loc_contract(TDD(temp_node1),temp_tdd2,var_cont)
            tdd1.unique_table[cont_level][key1]=temp_tdd1.node
            tdd1.unique_table[cont_level][key1].weight=temp_tdd1.weight
        tdd1.weight=tdd1.weight*w1*w2
        return tdd1
#     else:
#         x=v2
#         low=loc_contract(Slicing(tdd1,x,0),Slicing(tdd2,x,0),var_cont)
#         high=loc_contract(Slicing(tdd1,x,1),Slicing(tdd2,x,1),var_cont)
#         tdd=normalize(x,low,high)
#         insert_2_computed_table(['*',tdd1,tdd2,tuple(var_cont)],tdd)
#         tdd.weight=tdd.weight*w1*w2
#         return tdd
    
def contract_2_tdd(tdd1,tdd2):
    var_out,var_cont=get_contract_index(tdd1,tdd2)
    res=contract(tdd1,tdd2,var_cont)
    res.index_set=var_out
    return res
    
def contract(tdd1,tdd2,var_cont):
    """The contraction of two TDDs"""
    global global_index_order
    v1=tdd1.node.key
    v2=tdd2.node.key
    term=Find_Or_Add_Unique_table(1,0,0,None,None)
         
    if v1==1 and v2==1:
        weig=(2**len(var_cont))*tdd1.weight*tdd2.weight
        tdd=TDD(term)
        if get_int_key(weig)==(0,0):
            tdd.weight=0
        else:
            tdd.weight=weig
        return tdd

    if v1==1:
        if len(var_cont)==0:
            weig=tdd1.weight*tdd2.weight
            if get_int_key(weig)==(0,0):
                tdd=TDD(term)
                tdd.weight=0
                return tdd
            else:
                node=tdd2.node
                tdd=TDD(node)
                tdd.weight=weig
                return tdd
            
    if v2==1:
        return contract(tdd2,tdd1)
    
    w1=tdd1.weight
    w2=tdd2.weight
    tdd1.weight=1
    tdd2.weight=1
    
    if find_computed_table(['*',tdd1,tdd2,tuple(var_cont)]):
        tdd = find_computed_table(['*',tdd1,tdd2,tuple(var_cont)])
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
    if global_index_order.index(v1)<=global_index_order.index(v2):
        x=v1
    else:
        x=v2
        
    if not x in var_cont:
        low=contract(Slicing(tdd1,x,0),Slicing(tdd2,x,0),var_cont)
        high=contract(Slicing(tdd1,x,1),Slicing(tdd2,x,1),var_cont)
        tdd=normalize(x,low,high)
        insert_2_computed_table(['*',tdd1,tdd2,tuple(var_cont)],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
    else:
        new_var_cont=copy.copy(var_cont)
        new_var_cont.remove(x)
        low=contract(Slicing(tdd1,x,0),Slicing(tdd2,x,0),new_var_cont)
        high=contract(Slicing(tdd1,x,1),Slicing(tdd2,x,1),new_var_cont)
        tdd=add(low,high)
        insert_2_computed_table(['*',tdd1,tdd2,tuple(var_cont)],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    

    
    
def Slicing(tdd,x,c):
    """Slice a TDD with respect to x=c"""
    global global_index_order
    
    v=tdd.node.key
    
    temp_index_set=[]
    for var in tdd.index_set:
        if var.key !=x:
            temp_index_set.append(var)
            
    temp_index_set2=[]
    for var in tdd.index_set:
        if var.key !=v:
            temp_index_set2.append(var)            
    
    if find_computed_table(['s',tdd,x,c]):
        res = find_computed_table(['s',tdd,x,c])
        res.index_set = temp_index_set
        return res
    
    if not isinstance(v,str) or global_index_order.index(v)>global_index_order.index(x):
        res = copy.copy(tdd)
        res.index_set = temp_index_set
        insert_2_computed_table(['s',tdd,x,c],res)
        return res
    term=Find_Or_Add_Unique_table(1,0,0,None,None)
    leftweight=tdd.node.out_weight[0]*tdd.weight
    if get_int_key(leftweight)==(0,0):
        leftChild=TDD(term)
        leftChild.weight=0
    else:
        leftChild=TDD(tdd.node.successor[0])
        leftChild.weight=leftweight
    rightweight=tdd.node.out_weight[1]*tdd.weight
    if get_int_key(rightweight)==(0,0):
        rightChild=TDD(term)
        rightChild.weight=0
    else:
        rightChild=TDD(tdd.node.successor[1])
        rightChild.weight=rightweight            
    leftChild.index_set=temp_index_set2
    rightChild.index_set=temp_index_set2
    
    if v==x:
        if c==0:
            return leftChild
        else:
            return rightChild

    low=Slicing(leftChild,x,c)
    high=Slicing(rightChild,x,c)
    res=normalize(v,low,high)
    res.index_set = temp_index_set
    insert_2_computed_table(['s',tdd,x,c],res)
    return res

def add(tdd1,tdd2):
    """The apply function of two TDDs. Mostly, it is used to do addition here."""
    global global_index_order    
    
    v1=tdd1.node.key
    v2=tdd2.node.key
    if find_computed_table(['+',tdd1,tdd2]):
        return find_computed_table(['+',tdd1,tdd2]) 
    
    term=Find_Or_Add_Unique_table(1,0,0,None,None)

    if tdd1.node==tdd2.node:
        weig=tdd1.weight+tdd2.weight
        if get_int_key(weig)==(0,0):
            res=TDD(term)
            res.weight=0
            return res
        else:
            res=TDD(tdd1.node)
            res.weight=weig
            insert_2_computed_table(['+',tdd1,tdd2],res)
            return res

    if isinstance(v1,str) and not isinstance(v2,str):
        x=v1        
    elif isinstance(v2,str) and not isinstance(v1,str):
        x=v2    
    elif global_index_order.index(v1)<=global_index_order.index(v2):
        x=v1
    else:
        x=v2
        
    low=add(Slicing(tdd1,x,0),Slicing(tdd2,x,0))
    high=add(Slicing(tdd1,x,1),Slicing(tdd2,x,1))
    res = normalize(x,low,high)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res