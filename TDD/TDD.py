import numpy as np
import copy
import time
"""Define global variables"""
computed_table = dict()
unique_table = dict()
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
        return global_index_order[self.key] < global_index_order[other.key]
    def __str__(self):
        return str((self.key,self.idx))
    
class Node:
    """To define the node of TDD"""
    def __init__(self,key):
        self.idx = 0
        self.key = key
        self.out_weight=[1]*2
        self.successor=[None]*2


class TDD:
    def __init__(self,node):
        """TDD"""
        self.weight=1
        
        self.index_set=[]
        
        self.key_2_index=dict()
        self.index_2_key=dict()
        
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
        temp.key_2_index=copy.copy(self.key_2_index)
        temp.index_2_key=copy.copy(self.index_2_key)
        return temp
    
    def __eq__(self,other):
        if self.node==other.node and get_int_key(self.weight)==get_int_key(other.weight):
            return True
        else:
            return False

        
def Ini_TDD(var_order=[]):
    """To initialize the unique_table,computed_table and set up a global index order"""
    global computed_table
    global unique_table
    global global_node_idx
    
    global_node_idx=0
    unique_table = dict()
    computed_table = dict()
    set_index_order(var_order)
#     print(global_index_order)
    return get_identity_tdd()

def get_identity_tdd():
    node = Find_Or_Add_Unique_table(-1)
    tdd = TDD(node)
    tdd.index_2_key={-1:-1}
    tdd.key_2_index={-1:-1}
    return tdd

def get_unique_table():
    return global_unique_table

def get_unique_table_num():
    return len(global_unique_table)

def set_index_order(var_order):
    global global_index_order
    global_index_order=dict()
    if isinstance(var_order,list):
        for k in range(len(var_order)):
            global_index_order[var_order[k]]=k
    if isinstance(var_order,dict):
        global_index_order = copy.copy(var_order)
    global_index_order[-1] = float('inf')
    
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

def Find_Or_Add_Unique_table(x,weight1=0,weight2=0,node1=None,node2=None):
    """To return a node if it already exist, creates a new node otherwise"""
    global global_node_idx,unique_table
    
    if x==-1:
        if unique_table.__contains__(x):
            return unique_table[x]
        else:
            res=Node(x)
            res.idx=0
            unique_table[x]=res
        return res
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
    return res



def normalize(x,low,high):
    """The normalize and reduce procedure"""
    if high==low:
        return high
    weig1=low.weight
    weig2=high.weight
    epi=0.000001

    if get_int_key(weig1)==(0,0) and get_int_key(weig2)==(0,0):
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        res.weight=0
        return res
    elif get_int_key(weig1)==(0,0):
        node=Find_Or_Add_Unique_table(-1)
        low=TDD(node)
        weig1=0
    elif get_int_key(weig2)==(0,0):
        node=Find_Or_Add_Unique_table(-1)
        high=TDD(node)
        weig2=0
        
    if np.around(abs(weig1)/epi)>=np.around(abs(weig2)/epi):
        weig=weig1
    else:
        weig=weig2

    weig1=weig1/weig
    weig2=weig2/weig
    node=Find_Or_Add_Unique_table(x,weig1,weig2,low.node,high.node)
    res=TDD(node)
    res.weight=weig
    return res
        
        
def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table
    if item[0]=='s':
        temp_key=item[1].index_2_key[item[2]]
        the_key=('s',get_int_key(item[1].weight),item[1].node,temp_key,item[3])
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
    elif item[0] == '+':
        the_key=('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
        the_key=('+',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
    else:
        temp_key=(tuple(item[3][0]),tuple(item[3][1]))
        temp_key2=get_hash_key(item[1].index_2_key,item[2].index_2_key)
        the_key=('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,temp_key,temp_key2)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
        temp_key=(tuple(item[3][1]),tuple(item[3][0]))
        temp_key2=get_hash_key(item[2].index_2_key,item[1].index_2_key)
        the_key=('*',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node,temp_key,temp_key2)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            return tdd
    return None


def get_hash_key(idx_2_key1,idx_2_key2):
    A=set(idx_2_key1.keys())|set(idx_2_key2.keys())
    index_sort=[]
    res=[]
    for k in A:
        index_sort.append((global_index_order[k],k))
    index_sort.sort()
    
    for k in index_sort:
        if k[1] in idx_2_key1 and k[1] in idx_2_key2:
            res.append((1,2))
        elif k[1] in idx_2_key1:
            res.append(1)
        else:
            res.append(2)
    return tuple(res)

def insert_2_computed_table(item,res):
    """To insert an item to the computed table"""
    global computed_table
    if item[0]=='s':
        temp_key=item[1].index_2_key[item[2]]
        the_key = ('s',get_int_key(item[1].weight),item[1].node,temp_key,item[3])
    elif item[0] == '+':
#         temp_key=get_hash_key(item[1].index_2_key,item[2].index_2_key)
        the_key = ('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
    else:
        temp_key=(tuple(item[3][0]),tuple(item[3][1]))
        temp_key2=get_hash_key(item[1].index_2_key,item[2].index_2_key)
        the_key = ('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,temp_key,temp_key2)
#         print(temp_key)
#         print(temp_key2)
    computed_table[the_key] = (res.weight,res.node)
    

def Single_qubit_gate_2TDD(U,var):
    """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
#     print('xxxx')
#     for k in var:
#         print(k)
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    if var[0]<var[1]:
        idx_2_key[var[0].key]=1
        idx_2_key[var[1].key]=0
        key_2_idx[0]=var[1].key
        key_2_idx[1]=var[0].key
    else:
        idx_2_key[var[0].key]=0
        idx_2_key[var[1].key]=1
        key_2_idx[0]=var[0].key
        key_2_idx[1]=var[1].key 
    
    res=get_tdd(U,[var[1],var[0]],idx_2_key) 
    res.index_set=var
    res.index_2_key=idx_2_key
    res.key_2_index=key_2_idx
    return res 

def diag_matrix_2_TDD(U,var):
    term=Find_Or_Add_Unique_table(-1)
    if get_int_key(U[0][0])==get_int_key(U[1][1]):
        res=TDD(term)
        res.weight=U[0][0]
    else:
        low=TDD(term)
        low.weight=U[0][0]
        high=TDD(term)
        high.weight=U[1][1]
        res=normalize(0, low, high)
    res.index_set=var
    res.index_2_key={-1:-1,var[0].key:0}
    res.key_2_index={-1:-1,0:var[0].key}
    return res

def cnot_2_TDD(var,case=1):
#     print('ccccc')
#     for k in var:
#         print(k)
    
    if case==2:
        term=Find_Or_Add_Unique_table(-1)
        res=TDD(term)
        res.index_set = [var[0],var[1],var[2]]
        res.index_2_key={-1:-1,var[0].key:0}
        res.key_2_index={-1:-1,0:var[0].key}
        return res
    XOR=np.zeros((2,2,2))
    XOR[0][0][0]=XOR[0][1][1]=XOR[1][0][1]=XOR[1][1][0]=1
    
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    
    new_var=[var[0],var[3],var[4]]
    max_var=max(new_var)
    idx_2_key[max_var.key]=0
    key_2_idx[0]=max_var.key
    new_var.remove(max_var)
    max_var=max(new_var)
    idx_2_key[max_var.key]=1
    key_2_idx[1]=max_var.key
    new_var.remove(max_var)
    max_var=max(new_var)
    idx_2_key[max_var.key]=2
    key_2_idx[2]=max_var.key
    res=get_tdd(XOR,[var[0],var[3],var[4]],idx_2_key)
    res.index_2_key=idx_2_key
    res.key_2_index=key_2_idx
    if case==1:
        res.index_set=[var[0],var[2],var[3],var[4]]
    else:
        res.index_set=[var[1],var[3],var[4]]
    return res

def Two_qubit_gate_2TDD(U,var):
    """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
    U=U.reshape(2,2,2,2)
    return get_tdd(U,[var[3],var[1],var[2],var[0]]) 
    
def get_tdd(U,var,idx_2_key):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    if sum(U.shape)==U_dim:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
        return res
    min_index=min(var)
    x=min_index.key
    min_pos=var.index(min_index)
    new_var=copy.copy(var)
    new_var[min_pos]=Index(-1)
    split_U=np.split(U,2,min_pos)
    low=get_tdd(split_U[0],new_var,idx_2_key)
    high=get_tdd(split_U[1],new_var,idx_2_key)
    tdd = normalize(idx_2_key[x], low, high)
    return tdd

    
def np_2_tdd(U,split_pos=None):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    if sum(U.shape)==U_dim:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
        return res
    if split_pos==None:
        split_pos=U_dim-1
    split_U=np.split(U,2,split_pos)
    low=np_2_tdd(split_U[0],split_pos-1)
    high=np_2_tdd(split_U[1],split_pos-1)
    tdd = normalize(split_pos, low, high)
    return tdd
    
    
def get_contract_index(tdd1,tdd2):    
    var_out=[]
    var_cont=[]
    for var in tdd1.index_set:
        if var in tdd2.index_set:
            if not var.key in var_cont:
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
            var_temp.append((global_index_order[var],var))
    var_temp.sort()
    var_cont=[]
    
    for item in var_temp:
        var_cont.append(item[1])
    
    return var_out,var_cont

def cont(tdd1,tdd2):
    var_out,var_cont=get_contract_index(tdd1,tdd2)
    var_out.sort()
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    n=0
    for k in range(len(var_out)-1,-1,-1):
        if not var_out[k].key in idx_2_key:
            idx_2_key[var_out[k].key]=n
            key_2_idx[n]=var_out[k].key
            n+=1
    new_var_cont=[[],[]]
    for k in var_cont:
        new_var_cont[0].append(tdd1.index_2_key[k])
        new_var_cont[1].append(tdd2.index_2_key[k]) 
    tdd=contract(tdd1,tdd2,new_var_cont,idx_2_key)
    tdd.index_set=var_out
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
#     print('=====================================')
#     for k in tdd1.index_set:
#         print(k)
#     print(tdd1.index_2_key)
#     print(tdd1.key_2_index)
#     print('------------------------------')
#     for k in tdd2.index_set:
#         print(k)
#     print(tdd2.index_2_key)
#     print(tdd2.key_2_index)
#     print('------------------------------')
#     for k in tdd.index_set:
#         print(k)
#     print(tdd.index_2_key)
#     print(tdd.key_2_index)
#     print('=====================================')
    return tdd
    
    
def contract(tdd1,tdd2,var_cont,idx_2_key):
    """The contraction of two TDDs, var_cont is in the form [[4,1],[3,2]]"""
    
    k1=tdd1.node.key
    k2=tdd2.node.key
    v1=tdd1.key_2_index[k1]
    v2=tdd2.key_2_index[k2]
    
#     print('---------')
#     print(k1,v1)
#     print(k2,v2)
#     print(var_cont)
#     print('---------')
    
    if k1==-1 and k2==-1:
        weig=(2**len(var_cont[0]))*tdd1.weight*tdd2.weight
        term=Find_Or_Add_Unique_table(-1)
        tdd=TDD(term)
        if get_int_key(weig)==(0,0):
            tdd.weight=0
        else:
            tdd.weight=weig
        return tdd

    if k1==-1:
        if len(var_cont[0])==0 and idx_2_key[v2]==k2:
            weig=tdd1.weight*tdd2.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                tdd=TDD(term)
                tdd.weight=0
            else:
                tdd=TDD(tdd2.node)
                tdd.weight=weig
            return tdd
            
    if k2==-1:
        if len(var_cont[0])==0 and idx_2_key[v1]==k1:
            weig=tdd1.weight*tdd2.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                tdd=TDD(term)
                tdd.weight=0
            else:
                tdd=TDD(tdd1.node)
                tdd.weight=weig
            return tdd
    
    w1=tdd1.weight
    w2=tdd2.weight
    tdd1.weight=1
    tdd2.weight=1
    
    if find_computed_table(['*',tdd1,tdd2,var_cont]):
        tdd = find_computed_table(['*',tdd1,tdd2,var_cont])
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
    global global_index_order
    
    if global_index_order[v1]<=global_index_order[v2]:
        t=0
        k=k1
        x=v1
    else:
        t=1
        k=k2
        x=v2
#     print(t,k,x,var_cont[t])
        
    if not k in var_cont[t]:
        low=contract(Slicing1(tdd1,x,0),Slicing1(tdd2,x,0),var_cont,idx_2_key)
        high=contract(Slicing1(tdd1,x,1),Slicing1(tdd2,x,1),var_cont,idx_2_key)
        tdd=normalize(idx_2_key[x],low,high)
        insert_2_computed_table(['*',tdd1,tdd2,var_cont],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
    else:
        new_var_cont=[copy.copy(var_cont[0]),copy.copy(var_cont[1])]
        new_var_cont[0].remove(tdd1.index_2_key[x])
        new_var_cont[1].remove(tdd2.index_2_key[x])
        low=contract(Slicing1(tdd1,x,0),Slicing1(tdd2,x,0),new_var_cont,idx_2_key)
        high=contract(Slicing1(tdd1,x,1),Slicing1(tdd2,x,1),new_var_cont,idx_2_key)
        tdd=add(low,high)
        insert_2_computed_table(['*',tdd1,tdd2,var_cont],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
def Slicing(tdd,x,c):
    """Slice a TDD with respect to x=c"""
    global global_index_order
    
    k=tdd.node.key
    v=tdd.key_2_index[k]
    
    if k==-1:
        return tdd.self_copy()
    
    if global_index_order[v]>global_index_order[x]:
        return tdd.self_copy()
    
    if not x in tdd.index_2_key:
        return tdd.self_copy()
    
#     if find_computed_table(['s',tdd,x,c]):
#         return find_computed_table(['s',tdd,x,c])
    
    if v==x:
        if c==0:
            weig=tdd.node.out_weight[0]*tdd.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[0])
                res.weight=weig
            res.key_2_index=copy.copy(tdd.key_2_index)
            res.index_2_key=copy.copy(tdd.index_2_key)
            res.key_2_index.pop(k)
            res.index_2_key.pop(x)
            return res
        if c==1:
            weig=tdd.node.out_weight[1]*tdd.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[1])
                res.weight=weig
            res.key_2_index=copy.copy(tdd.key_2_index)
            res.index_2_key=copy.copy(tdd.index_2_key)
            res.key_2_index.pop(k)
            res.index_2_key.pop(x)
            return res
        

    leftweight=tdd.node.out_weight[0]*tdd.weight
    if get_int_key(leftweight)==(0,0):
        term=Find_Or_Add_Unique_table(-1)
        leftChild=TDD(term)
        leftChild.weight=0
    else:
        leftChild=TDD(tdd.node.successor[0])
        leftChild.weight=leftweight
        
    rightweight=tdd.node.out_weight[1]*tdd.weight
    if get_int_key(rightweight)==(0,0):
        term=Find_Or_Add_Unique_table(-1)
        rightChild=TDD(term)
        rightChild.weight=0
    else:
        rightChild=TDD(tdd.node.successor[1])
        rightChild.weight=rightweight 

    low=Slicing(leftChild,x,c)
    high=Slicing(rightChild,x,c)
    res=normalize(k,low,high)
#     insert_2_computed_table(['s',tdd,x,c],res)
    res.key_2_index=copy.copy(tdd.key_2_index)
    res.index_2_key=copy.copy(tdd.index_2_key)
    res.key_2_index.pop(tdd.index_2_key[x])
    res.index_2_key.pop(x)
    return res
    
def Slicing1(tdd,x,c):
    """Slice a TDD with respect to x=c"""
    global global_index_order
    
    k=tdd.node.key
    v=tdd.key_2_index[k]
    
    if k==-1:
        return tdd.self_copy()
    
    if global_index_order[v]>global_index_order[x]:
        return tdd.self_copy()
    
    if not x in tdd.index_2_key:
        return tdd.self_copy()
    
    if v==x:
        if c==0:
            weig=tdd.node.out_weight[0]
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[0])
                res.weight=weig
            res.key_2_index=tdd.key_2_index
            res.index_2_key=tdd.index_2_key
            return res
        if c==1:
            weig=tdd.node.out_weight[1]
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[1])
                res.weight=weig
            res.key_2_index=tdd.key_2_index
            res.index_2_key=tdd.index_2_key
            return res
    else:
        print("Not supported yet!!!")
        
def Slicing2(tdd,x,c):
    """Slice a TDD with respect to x=c"""

    k=tdd.node.key
    
    if k==-1:
        return tdd.self_copy()
    
    if k<x:
        return tdd.self_copy()
    
    if k==x:
        if c==0:
            weig=tdd.node.out_weight[0]*tdd.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[0])
                res.weight=weig
            return res
        if c==1:
            weig=tdd.node.out_weight[1]*tdd.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                res=TDD(tdd.node.successor[1])
                res.weight=weig
            return res
    else:
        print("Not supported yet!!!")


def add(tdd1,tdd2):
    """The apply function of two TDDs. Mostly, it is used to do addition here."""
    global global_index_order    
    
    k1=tdd1.node.key
    k2=tdd2.node.key
    
#     print("aaaaaadddddddddd")
#     print(k1)
#     print(k2)
#     print("aaaaaadddddddddd")
    if tdd1.weight==0:
        return tdd2.self_copy()
    
    if tdd2.weight==0:
        return tdd1.self_copy()
    
    if tdd1.node==tdd2.node:
        weig=tdd1.weight+tdd2.weight
        if get_int_key(weig)==(0,0):
            term=Find_Or_Add_Unique_table(-1)
            res=TDD(term)
            res.weight=0
            return res
        else:
            res=tdd1.self_copy()
            res.weight=weig
            return res
        
    if find_computed_table(['+',tdd1,tdd2]):
        return find_computed_table(['+',tdd1,tdd2])
    
    if k1>=k2:
        x=k1
    else:
        x=k2
        
    low=add(Slicing2(tdd1,x,0),Slicing2(tdd2,x,0))
    high=add(Slicing2(tdd1,x,1),Slicing2(tdd2,x,1))
    res = normalize(x,low,high)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res