import numpy as np
import copy
import time
"""Define global variables"""
computed_table = dict()
unique_table = dict()
global_index_order = dict()
global_node_idx=0
add_find_time=0
add_hit_time=0
cont_find_time=0
cont_hit_time=0

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
    def __init__(self,key,num=2):
        self.idx = 0
        self.key = key
        self.succ_num=num
        self.out_weight=[1]*num
        self.successor=[None]*num


class TDD:
    def __init__(self,node):
        """TDD"""
        self.weight=1
        
        self.index_set=[]
        
        self.key_2_index=dict()
        self.index_2_key=dict()
        self.key_width=dict()
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
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time
    global_node_idx=0
    unique_table = dict()
    computed_table = dict()
    add_find_time=0
    add_hit_time=0
    cont_find_time=0
    cont_hit_time=0
    set_index_order(var_order)
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
        for k in range(node.succ_num):
            if node.successor[k]:
                node_set = get_node_set(node.successor[k],node_set)
    return node_set

def Find_Or_Add_Unique_table(x,weigs=[],succ_nodes=[]):
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
    temp_key=[x]
    for k in range(len(weigs)):
        temp_key.append(get_int_key(weigs[k]))
        temp_key.append(succ_nodes[k])
    temp_key=tuple(temp_key)
    if temp_key in unique_table:
        return unique_table[temp_key]
    else:
        res=Node(x,len(succ_nodes))
        global_node_idx+=1
        res.idx=global_node_idx
        res.out_weight=weigs
        res.successor=succ_nodes
        unique_table[temp_key]=res
    return res


def normalize(x,the_successors):
    """The normalize and reduce procedure"""
    all_equal=True
    for k in range(1,len(the_successors)):
        if the_successors[k]!=the_successors[0]:
            all_equal=False
            break
    if all_equal:
        return the_successors[0]
    
    weigs=[succ.weight for succ in the_successors]

    all_zeros=True
    for k in range(len(the_successors)):
        if get_int_key(weigs[k])!=(0,0):
            all_zeros=False
            break
    if all_zeros:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        res.weight=0
        return res
    for k in range(len(the_successors)):
        if get_int_key(weigs[k])==(0,0):
            node=Find_Or_Add_Unique_table(-1)
            the_successors[k]=TDD(node)
            the_successors[k].weight=weigs[k]=0

    epi=0.000001
    
    weigs_abs=[np.around(abs(weig)/epi) for weig in weigs]
    weig_max=weigs[weigs_abs.index(max(weigs_abs))]
    weigs=[weig/weig_max for weig in weigs]
    succ_nodes=[succ.node for succ in the_successors]
    node=Find_Or_Add_Unique_table(x,weigs,succ_nodes)
    res=TDD(node)
    res.weight=weig_max
    return res

def get_count():
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time
    print("add:",add_hit_time,'/',add_find_time,'/',add_hit_time/add_find_time)
    print("cont:",cont_hit_time,"/",cont_find_time,"/",cont_hit_time/cont_find_time)

def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table,add_find_time,add_hit_time,cont_find_time,cont_hit_time
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
        add_find_time+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            add_hit_time+=1
            return tdd
        the_key=('+',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node)
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            add_hit_time+=1
            return tdd
    else:
        the_key=('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3][0],item[3][1],item[4])
        cont_find_time+=1
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            cont_hit_time+=1            
            return tdd
        the_key=('*',get_int_key(item[2].weight),item[2].node,get_int_key(item[1].weight),item[1].node,item[3][1],item[3][0],item[4])
        if computed_table.__contains__(the_key):
            res = computed_table[the_key]
            tdd = TDD(res[1])
            tdd.weight = res[0]
            cont_hit_time+=1            
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
        the_key = ('*',get_int_key(item[1].weight),item[1].node,get_int_key(item[2].weight),item[2].node,item[3][0],item[3][1],item[4])
    computed_table[the_key] = (res.weight,res.node)
    

def Single_qubit_gate_2TDD(U,var):
    """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
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
        res=normalize(0, [low, high])
    res.index_set=var
    res.index_2_key={-1:-1,var[0].key:0}
    res.key_2_index={-1:-1,0:var[0].key}
    res.key_width[0]=2
    return res

def diag_matrix_2_TDD2(U,var):
    if var[0]<var[2]:
        x1=var[0].key
        x0=var[2].key
        low = diag_matrix_2_TDD(U[:2,:2],var[2:])
        high = diag_matrix_2_TDD(U[2:,2:],var[2:])          
    else:
        x1=var[2].key
        x0=var[0].key
        low = diag_matrix_2_TDD(np.diag([U[0][0],U[2,2]]),var[:2])
        high = diag_matrix_2_TDD(np.diag([U[1][1],U[3,3]]),var[:2])
       
    
    if low==high:
        res=low
    else:
        res=normalize(1,[low,high])
        
    res.index_set=var
    res.index_2_key={-1:-1,x0:0,x1:1}
    res.key_2_index={-1:-1,0:x0,1:x1}
    res.key_width[0]=res.key_width[1]=2
    return res


def cnot_2_TDD(var,case=1):
    
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
    res.key_width[0]=res.key_width[1]=res.key_width[2]=2
    return res

def Two_qubit_gate_2TDD(U,var):
    """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
    U=U.reshape(2,2,2,2)
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    
    new_var=[var[0],var[1],var[2],var[3]]
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
    new_var.remove(max_var)
    max_var=max(new_var)
    idx_2_key[max_var.key]=3
    key_2_idx[3]=max_var.key
    res=get_tdd(U,[var[3],var[1],var[2],var[0]],idx_2_key) 
    res.index_2_key=idx_2_key
    res.key_2_index=key_2_idx
    res.index_set=[var[0],var[1],var[2],var[3]]
    res.key_width[0]=res.key_width[1]=res.key_width[2]=res.key_width[3]=2
    return res
    
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
    tdd = normalize(idx_2_key[x], [low,high])
    return tdd

    
def np_2_tdd(U,split_pos=None):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    U_shape=U.shape
    if sum(U_shape)==U_dim:
        node=Find_Or_Add_Unique_table(-1)
        res=TDD(node)
        for k in range(U_dim):
            U=U[0]
        res.weight=U
        return res
    if split_pos==None:
        split_pos=U_dim-1
        
    split_U=np.split(U,U_shape[split_pos],split_pos)
    the_successors=[]
    for k in range(U_shape[split_pos]):
        res=np_2_tdd(split_U[k],split_pos-1)
        the_successors.append(res)
    tdd = normalize(split_pos,the_successors)
    for k in range(len(U_shape)):
        tdd.key_width[k]=U_shape[k]
    return tdd
    
def tdd_2_np(tdd,split_pos=None):    
    if split_pos==None:
        split_pos=tdd.node.key
    if split_pos==-1:
        return tdd.weight
    else:
        the_succs=[]
        for k in range(tdd.key_width[split_pos]):
            succ=Slicing(tdd,split_pos,k)
            succ.key_width=tdd.key_width
            temp_res=tdd_2_np(succ,split_pos-1)
            the_succs.append(temp_res)
        res=np.stack(tuple(the_succs), axis=split_pos)
        res=res*tdd.weight
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
        
    cont_order[0].append(float('inf'))
    
    for k in range(len(tdd2.key_2_index)-1):     
        v=tdd2.key_2_index[k]
        if v in idx_2_key:
            key_2_new_key[1].append(idx_2_key[v])
        else:
            key_2_new_key[1].append('c')
        cont_order[1].append(global_index_order[v])
    cont_order[1].append(float('inf'))

    tdd=contract(tdd1,tdd2,key_2_new_key,cont_order,len(set(var_cont_idx)))
    tdd.index_set=var_out
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
    return tdd
    
def cont2(tdd1,tdd2,cont_var):
    """cont_var is in the form [[0],[3]]"""
    key_2_new_key=[[],[]]
    cont_order=[[],[]]
    cont_num=len(cont_var[0])
    num1=0
    num2=0
    cont_var[0].append(0)
    cont_var[1].append(0)
    for k in range(cont_num):
        for k1 in range(cont_var[0][k-1],cont_var[0][k]):
            key_2_new_key[0].append(num1)
            num1+=1
            cont_order[0].append(num2)
            num2+=1
        
        for k2 in range(cont_var[1][k-1],cont_var[1][k]):
            key_2_new_key[1].append(num1)
            num1+=1
            cont_order[1].append(num2)
            num2+=1
        cont_order[0].append(num2)
        cont_order[1].append(num2)
        num2+=1
        key_2_new_key[0].append('c')
        key_2_new_key[1].append('c')
        
    for k1 in range(cont_var[0][cont_num-1],tdd1.node.key):
        key_2_new_key[0].append(num1)
        num1+=1
        cont_order[0].append(num2)
        num2+=1
    for k2 in range(cont_var[1][cont_num-1],tdd2.node.key):
        key_2_new_key[1].append(num1)
        num1+=1
        cont_order[1].append(num2)
        num2+=1
    the_max=max(max(cont_order[0],cont_order[1]))
    cont_order[0]=[the_max-k for k in cont_order[0]]
    cont_order[1]=[the_max-k for k in cont_order[1]]
    cont_order[0].append(float('inf'))
    cont_order[1].append(float('inf'))
#     print(key_2_new_key,cont_order)
    return contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num)


def contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num):
    """The contraction of two TDDs, var_cont is in the form [[4,1],[3,2]]"""
    
    k1=tdd1.node.key
    k2=tdd2.node.key
    w1=tdd1.weight
    w2=tdd2.weight
    
    if k1==-1 and k2==-1:
        if w1==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        if w2==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        tdd=TDD(tdd1.node)
        tdd.weight=w1*w2
        if cont_num>0:
            tdd.weight*=2**cont_num
        return tdd

    if k1==-1:
        if w1==0:
            tdd=TDD(tdd1.node)
            tdd.weight=0
            return tdd
        if cont_num ==0 and key_2_new_key[1][k2]==k2:
            tdd=TDD(tdd2.node)
            tdd.weight=w1*w2
            return tdd
            
    if k2==-1:
        if w2==0:
            tdd=TDD(tdd2.node)
            tdd.weight=0
            return tdd        
        if cont_num ==0 and key_2_new_key[0][k1]==k1:
            tdd=TDD(tdd1.node)
            tdd.weight=w1*w2
            return tdd
    
    tdd1.weight=1
    tdd2.weight=1
    
    temp_key_2_new_key=[]
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[0][:(k1+1)]]))
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[1][:(k2+1)]]))
    
    tdd=find_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num])
    if tdd:
        tdd.weight=tdd.weight*w1*w2
        return tdd
                
    if cont_order[0][k1]<cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
    elif cont_order[0][k1]==cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
    else:
        the_key=key_2_new_key[1][k2]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
            tdd.weight=tdd.weight*w1*w2
        else:
            tdd=TDD(Find_Or_Add_Unique_table(-1))
            tdd.weight=0
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                tdd=add(tdd,res)
            insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
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
        res=TDD(tdd.node.successor[c])
        res.weight=tdd.node.out_weight[c]
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
        res=TDD(tdd.node.successor[c])
        res.weight=tdd.node.out_weight[c]*tdd.weight
        return res
    else:
        print("Not supported yet!!!")        
        
        

def add(tdd1,tdd2):
    """The apply function of two TDDs. Mostly, it is used to do addition here."""
    global global_index_order    
    
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
            res=TDD(tdd1.node)
            res.weight=weig
            return res
        
    if find_computed_table(['+',tdd1,tdd2]):
        return find_computed_table(['+',tdd1,tdd2])
    the_successors=[]
    if k1>k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            res=add(Slicing2(tdd1,x,k),tdd2)
            the_successors.append(res)
    elif k1==k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            res=add(Slicing2(tdd1,x,k),Slicing2(tdd2,x,k))
            the_successors.append(res)        
    else:
        x=k2
        for k in range(tdd2.node.succ_num):
            res=add(tdd1,Slicing2(tdd2,x,k))
            the_successors.append(res)
            
    res = normalize(x,the_successors)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res