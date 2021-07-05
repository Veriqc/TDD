import numpy as np
import copy
import time
"""Define global variables"""
computed_table = dict()
unique_table = dict()
node_table = dict()
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
        self.successor_idx=[0]*2
        self.successor=[None]*2

class TDD:
    def __init__(self,node):
        """Local TDD"""
        self.weight=1
        
        self.index_set=[]
        
        self.key_2_index=dict()
        self.index_2_key=dict()
        
        self.node_weights=dict()
        
        self.node_table=dict()
        
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
        temp.unique_table=copy.copy(unique_table)
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
    return unique_table

def get_unique_table_num():
    return len(unique_table)

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
        res.successor_idx=[node1.idx,node2.idx]
        res.successor=[node1,node2]
        unique_table[temp_key]=res
    return res

def add_2_node_table(k,node):
    global node_table
    if not k in node_table:
        node_table[k]=dict()
    if not node.idx in node_table[k]:
        node_table[k][node.idx]=node

def normalize(x,low,high):
    """The normalize and reduce procedure"""
    global node_table
    if high==low:
        add_2_node_table(x,high.node)
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
    add_2_node_table(x,node)
    for k in range(x-1,low.node.key,-1):
        if not k in node_table or not low.node.idx in node_table[k]:
            add_2_node_table(k,low.node)
        else:
            break
            
    for k in range(x-1,high.node.key,-1):
        if not k in node_table or not high.node.idx in node_table[k]:
            add_2_node_table(k,high.node)
        else:
            break           
    
    res=TDD(node)
    res.weight=weig
    return res

def global_normalize(tdd):
    global node_table
    node_table=dict()
    res=global_normalize2(tdd)
    res.index_set = tdd.index_set
    res.index_2_key=tdd.index_2_key
    res.key_2_index=tdd.key_2_index
    return res

def global_normalize2(tdd):
    term=Find_Or_Add_Unique_table(-1)
    if tdd.node.key==-1:
        res=TDD(term)
        res.weight=tdd.weight
    else:
        x=tdd.node.key
        if not x-1 in tdd.node_table or not tdd.node.successor_idx[0] in tdd.node_table[x-1]:
            node1=term
        else:
            node1=tdd.node_table[x-1][tdd.node.successor_idx[0]]
        low=TDD(node1)
        low.node_table=tdd.node_table
        low.node_weights=tdd.node_weights
        low=global_normalize(low)
        low.weight=low.weight*tdd.node.out_weight[0]
        if (x-1,node1) in tdd.node_weights:
            low.weight*=tdd.node_weights[(x-1,node1)]
        if not x-1 in tdd.node_table or not tdd.node.successor_idx[1] in tdd.node_table[x-1]:
            node2=term
        else:
            node2=tdd.node_table[x-1][tdd.node.successor_idx[1]]                       
        high=TDD(node2)
        high.node_table=tdd.node_table
        high.node_weights=tdd.node_weights
        high=global_normalize(high)
        high.weight=high.weight*tdd.node.out_weight[1]
        if (x-1,node2) in tdd.node_weights:
            high.weight*=tdd.node_weights[(x-1,node2)]
        res=normalize(x,low,high)
        res.weight*=tdd.weight
    return res

        
cont_time=0
find_time=[0,0]
hit_time=[0,0]

def get_count():
    global computed_table,cont_time,find_time,hit_time
    print(cont_time,find_time,hit_time)

def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table,cont_time,find_time,hit_time
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
        temp_key0=tuple(item[3][0])
        temp_key1=tuple(item[3][1])
        the_key=('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,temp_key0,temp_key1)
        find_time[0]+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            hit_time[0]+=1            
            return tdd
        the_key=('*',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node,temp_key1,temp_key0)
        find_time[1]+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            hit_time[1]+=1            
            return tdd
    return None

def insert_2_computed_table(item,res):
    """To insert an item to the computed table"""
    global computed_table,cont_time,find_time,hit_time
    if item[0]=='s':
        temp_key=item[1].index_2_key[item[2]]
        the_key = ('s',get_int_key(item[1].weight),item[1].node,temp_key,item[3])
    elif item[0] == '+':
        the_key = ('+',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node)
    else:
        temp_key0=tuple(item[3][0])
        temp_key1=tuple(item[3][1])
        the_key = ('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,temp_key0,temp_key1)
        cont_time+=1
    computed_table[the_key] = (res.weight,res.node)
    

def Single_qubit_gate_2TDD(U,var):
    """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
    global node_table
    node_table=dict()
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
    res.node_table=node_table
    return res 

def diag_matrix_2_TDD(U,var):
    global node_table
    node_table=dict()
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
    res.node_table=node_table
    return res

def cnot_2_TDD(var,case=1):
    global node_table
    node_table=dict()    
    if case==2:
        term=Find_Or_Add_Unique_table(-1)
        res=TDD(term)
        res.index_set = [var[0],var[1],var[2]]
        res.index_2_key={-1:-1,var[0].key:0}
        res.key_2_index={-1:-1,0:var[0].key}
        res.node_table=node_table
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
    res.node_table=node_table
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
    global node_table
    U_dim=U.ndim
#     print(node_table)
    if sum(U.shape)==U_dim:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
#         if not -1 in node_table:
#             node_table[-1]=dict()
#         if not -1 in node_table[-1]:
#             node_table[-1][0]=node
        return res
    min_index=min(var)
    k=min_index.key
    min_pos=var.index(min_index)
    new_var=copy.copy(var)
    new_var[min_pos]=Index(-1)
    split_U=np.split(U,2,min_pos)
    low=get_tdd(split_U[0],new_var,idx_2_key)
    high=get_tdd(split_U[1],new_var,idx_2_key)
    x=idx_2_key[k]
    res = normalize(x, low, high)
#     if not x in node_table:
#         node_table[x]=dict()
#     if not res.node.idx in node_table[x]:
#         node_table[x][res.node.idx]=res.node
    return res
  
def np_2_tdd(U,split_pos=None):
    #transform a numpy ndarray to a tdd
    global node_table
    U_dim=U.ndim
    if split_pos==None:
        split_pos=U_dim-1
    if sum(U.shape)==U_dim:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
    else:
        split_U=np.split(U,2,split_pos)
        low=np_2_tdd(split_U[0],split_pos-1)
        high=np_2_tdd(split_U[1],split_pos-1)
        res = normalize(split_pos, low, high)
#     if not split_pos in node_table:
#         node_table[split_pos]=dict()
#     if not res.node.idx in node_table[split_pos]:
#         node_table[split_pos][res.node.idx]=res.node
    return res
    
    

def cont(tdd1,tdd2):
    var_cont=[var for var in tdd1.index_set if var in tdd2.index_set]
    var_out1=[var for var in tdd1.index_set if not var in var_cont]
    var_out2=[var for var in tdd2.index_set if not var in var_cont]
    var_out=var_out1+var_out2
    var_out.sort()
    var_out_idx=[var.key for var in var_out]
    var_cont_idx=[var.key for var in var_cont]
    var_cont_idx=[var for var in var_cont_idx if not var in var_out_idx]
    
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    
    n=0
    for k in range(len(var_out_idx)-1,-1,-1):
        if not var_out_idx[k] in idx_2_key:
            idx_2_key[var_out_idx[k]]=n
            key_2_idx[n]=var_out_idx[k]
            n+=1
        
    key_2_new_key=[[],[]]
    cont_order=[[],[]]
    for k in range(len(tdd1.key_2_index)-1):
        v=tdd1.key_2_index[k]
        if v in idx_2_key:
            key_2_new_key[0].append(idx_2_key[v])
        else:
            key_2_new_key[0].append('c')
        cont_order[0].append(global_index_order[v])
        
    key_2_new_key[0].append(-1)
    cont_order[0].append(float('inf'))

    for k in range(len(tdd2.key_2_index)-1):
        v=tdd2.key_2_index[k]
        if v in idx_2_key:
            key_2_new_key[1].append(idx_2_key[v])
        else:
            key_2_new_key[1].append('c')
        cont_order[1].append(global_index_order[v])
    key_2_new_key[1].append(-1)
    cont_order[1].append(float('inf'))
    tdd=loc_contract(tdd1,tdd2,key_2_new_key,cont_order,len(set(var_cont_idx)))
    tdd.index_set=var_out
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
    return tdd

def add_node_table(node_table1,node_table2):
    
    for k in node_table2:
        if not k in node_table1:
            node_table1[k]=node_table2[k]
        else:
            for k1 in node_table2[k]:
                if not k1 in node_table1[k]:
                    node_table1[k][k1]=node_table2[k][k1]

    return node_table1

def loc_contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num):
    """To local contract tdd1 and tdd2"""
    global global_index_order,node_table
    node_table=dict()
    k1=tdd1.node.key
    k2=tdd2.node.key
    
    w1=tdd1.weight
    w2=tdd2.weight
    tdd1.weight=1
    tdd2.weight=1
    

    if cont_num !=0 and key_2_new_key[0][k1]!='c' and cont_order[0][k1]<cont_order[1][k2]:
        cont_level=k1
        for k in range(k1-1,-2,-1):
            if cont_order[0][k]>=cont_order[1][k2] or key_2_new_key[0][k]=='c':
                cont_level=k
                break
        print(cont_level)
        new_node_table=dict()
        for k in range(k1,-1,-1):
            if key_2_new_key[0][k]!='c':
                new_node_table[key_2_new_key[0][k]]=tdd1.node_table[k]
        new_node_table[key_2_new_key[0][cont_level+1]-1]=tdd1.node_table[cont_level]
        
#         temp_node_table=dict()
#         for k in range(cont_level-1,-1,-1):
#             temp_node_table[k]=tdd1.node_table[k]
#             tdd1.node_table.pop(k) 

        for key1 in tdd1.node_table[cont_level]:
            temp_tdd1=TDD(tdd1.node_table[cont_level][key1])
            temp_tdd1.node_table=tdd1.node_table
#             for k in range(cont_level-1,-1,-1):
#                 temp_tdd1.node_table[k]=copy.copy(temp_node_table[k])
#             temp_tdd1.node_table[cont_level]={key1:tdd1.node_table[cont_level][key1]}
#             print(temp_tdd1.node_table)
            temp_tdd1 = contract(temp_tdd1,tdd2,key_2_new_key,cont_order,cont_num)
#             print(temp_tdd1.node.idx,temp_tdd1.node.key,temp_tdd1.node.out_weight)
            new_node_table[key_2_new_key[0][cont_level+1]-1][key1]=temp_tdd1.node
            for k in range(key_2_new_key[0][cont_level+1]-2,temp_tdd1.node.key-1,-1):
                add_2_node_table(k,temp_tdd1.node)
                
            if not temp_tdd1.weight==1:
                for k in range(key_2_new_key[0][cont_level+1]-1,temp_tdd1.node.key-1,-1):
                    tdd1.node_weights[(k,temp_tdd1.node)]=temp_tdd1.weight
                
        new_node_table=add_node_table(new_node_table,node_table)
        tdd1.node_table=new_node_table
        tdd1.weight=tdd1.weight*w1*w2
        return tdd1
    else:
        res = contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num)
        res.node_table=node_table
        return 


def contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num):
    """The contraction of two TDDs, var_cont is in the form [[4,1],[3,2]]"""
    global node_table
    
    k1=tdd1.node.key
    k2=tdd2.node.key
    w1=tdd1.weight
    w2=tdd2.weight
    if k1==-1 and k2==-1:
        weig=(2**cont_num)*w1*w2
        term=Find_Or_Add_Unique_table(-1)
        tdd=TDD(term)
        if get_int_key(weig)==(0,0):
            tdd.weight=0
        else:
            tdd.weight=weig
        return tdd

    if k1==-1:
        if w1==0:
            term=Find_Or_Add_Unique_table(-1)
            tdd=TDD(term)
            tdd.weight=0
            return tdd        
        if cont_num ==0 and key_2_new_key[1][k2]==k2:
            weig=w1*w2
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                tdd=TDD(term)
                tdd.weight=0
            else:
                tdd=TDD(tdd2.node)
                tdd.weight=weig
#                 node_table=add_node_table(node_table,tdd2.node_table)
            return tdd
            
    if k2==-1:
        if w1==0:
            term=Find_Or_Add_Unique_table(-1)
            tdd=TDD(term)
            tdd.weight=0
            return tdd        
        if cont_num ==0 and key_2_new_key[0][k1]==k1:
            weig=w1*w2
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                tdd=TDD(term)
                tdd.weight=0
            else:
                tdd=TDD(tdd1.node)
                tdd.weight=weig
#                 node_table=add_node_table(node_table,tdd1.node_table)
            return tdd
    
    tdd1.weight=1
    tdd2.weight=1
    
    if find_computed_table(['*',tdd1,tdd2,key_2_new_key]):
        tdd = find_computed_table(['*',tdd1,tdd2,key_2_new_key])
        tdd.weight=tdd.weight*w1*w2
        return tdd
                
                
    temp_key_2_new_key=[copy.copy(key_2_new_key[0]),copy.copy(key_2_new_key[1])]
    if cont_order[0][k1]<cont_order[1][k2]:
        case=0
        k=k1
        s0=k1
        s1=float('inf')
        temp_key_2_new_key[0].pop(s0)
    elif cont_order[0][k1]==cont_order[1][k2]:
        case=0
        k=k1
        s0=k1
        s1=k2
        temp_key_2_new_key[0].pop(s0)
        temp_key_2_new_key[1].pop(s1)
    else:
        case=1
        k=k2
        s0=float('inf')
        s1=k2
        temp_key_2_new_key[1].pop(s1)
            
        
    if key_2_new_key[case][k]!='c':
        low=contract(Slicing(tdd1,s0,0),Slicing(tdd2,s1,0),temp_key_2_new_key,cont_order,cont_num)
        high=contract(Slicing(tdd1,s0,1),Slicing(tdd2,s1,1),temp_key_2_new_key,cont_order,cont_num)
        tdd=normalize(key_2_new_key[case][k],low,high)
        insert_2_computed_table(['*',tdd1,tdd2,key_2_new_key],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
    else:
        low=contract(Slicing(tdd1,s0,0),Slicing(tdd2,s1,0),temp_key_2_new_key,cont_order,cont_num-1)
        high=contract(Slicing(tdd1,s0,1),Slicing(tdd2,s1,1),temp_key_2_new_key,cont_order,cont_num-1)
        tdd=add(low,high)
        insert_2_computed_table(['*',tdd1,tdd2,key_2_new_key],tdd)
        tdd.weight=tdd.weight*w1*w2
        return tdd
    
def Slicing(tdd,x,c):
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
                if not k-1 in tdd.node_table or not tdd.node.successor_idx[0] in tdd.node_table[k-1]:
                    node=Find_Or_Add_Unique_table(-1)
                else:
                    node=tdd.node_table[k-1][tdd.node.successor_idx[0]]                
                res=TDD(node)
                res.weight=weig
                res.node_table=tdd.node_table
            return res
        if c==1:
            weig=tdd.node.out_weight[1]*tdd.weight
            if get_int_key(weig)==(0,0):
                term=Find_Or_Add_Unique_table(-1)
                res=TDD(term)
                res.weight=0
            else:
                if not k-1 in tdd.node_table or not tdd.node.successor_idx[1] in tdd.node_table[k-1]:
                    node=Find_Or_Add_Unique_table(-1)
                else:
                    node=tdd.node_table[k-1][tdd.node.successor_idx[1]]                 
                res=TDD(node)
                res.weight=weig
                res.node_table=tdd.node_table
            return res
    else:
        print("Not supported yet!!!")

def add(tdd1,tdd2):
    """The apply function of two TDDs. Mostly, it is used to do addition here."""
    global global_index_order,node_table  
    
    k1=tdd1.node.key
    k2=tdd2.node.key
    
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
#             node_table=add_node_table(node_table,tdd1.node_table)
            return res
        
    if find_computed_table(['+',tdd1,tdd2]):
        return find_computed_table(['+',tdd1,tdd2])
    
    if k1>=k2:
        x=k1
    else:
        x=k2
        
    low=add(Slicing(tdd1,x,0),Slicing(tdd2,x,0))
    high=add(Slicing(tdd1,x,1),Slicing(tdd2,x,1))
    res = normalize(x,low,high)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res