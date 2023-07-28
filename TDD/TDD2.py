import numpy as np
import copy
import time
import random
from TDD.ComplexTable import *


"""在这个版本中node的succ直接是tdd"""

"""Define global variables"""
computed_table = dict()
unique_table = dict()
global_index_order = dict()
global_node_idx=0
add_find_time=0
add_hit_time=0
cont_find_time=0
cont_hit_time=0
add_hit_time2=0
# epi=1e-5

terminal_node = None
DDzero = None
DDone = None

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
        if global_index_order[self.key] < global_index_order[other.key]:
            return True
        elif self.key == other.key and self.idx<other.idx:
            return True
        
        return False
    
    def __str__(self):
        return str((self.key,self.idx))

    
class Node:
    """To define the node of TDD"""
    def __init__(self,key,num=2):
        self.idx = 0
        self.key = key
        self.succ_num=num
        self.succ = [None]*num
        self.meas_prob=[]
        self.ref_num = 0


class TDD:
    def __init__(self,node,weight=cn1):
        """TDD"""
        self.weight = weight

        self.index_set=[]
        
        self.key_2_index=dict()
        self.index_2_key=dict()
        self.key_width=dict() #Only used when change TDD to numpy
        
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
        temp.index_set = copy.copy(self.index_set)
        temp.key_2_index=copy.copy(self.key_2_index)
        temp.index_2_key=copy.copy(self.index_2_key)
        return temp
    
    def show(self,real_label=True):
        from graphviz import Digraph
        from IPython.display import Image 
        dot=Digraph(name='reduced_tree')
        dot=layout(self.node,self.key_2_index,dot,[],real_label)
        dot.node('-0','',shape='none')
        dot.edge('-0',str(self.node.idx),color="blue",label=str(complex(round(self.weight.r.val,2),round(self.weight.i.val,2))))
        dot.format = 'png'
        return Image(dot.render('output'))
    
    def to_array(self,var=[]):
        split_pos=0
        key_repeat_num=dict()
        var_idx=dict()       
        if var:
            for idx in var:
                if not idx.key in var_idx:
                    var_idx[idx.key]=1
                else:
                    var_idx[idx.key]+=1
        elif self.index_set:
            for idx in self.index_set:
                if not idx.key in var_idx:
                    var_idx[idx.key]=1
                else:
                    var_idx[idx.key]+=1
        if var:
            split_pos=len(var_idx)-1
        elif self.key_2_index:
            split_pos=max(self.key_2_index)
        else:
            split_pos=self.node.key
        orig_order=[]
        for k in range(split_pos+1):
            if k in self.key_2_index:
                if self.key_2_index[k] in var_idx:
                    key_repeat_num[k] = var_idx[self.key_2_index[k]]
            else:
                key_repeat_num[k]=1
            if k in self.key_2_index:
                for k1 in range(key_repeat_num[k]):
                    orig_order.append(self.key_2_index[k])
                     

        res = tdd_2_np(self,split_pos,key_repeat_num)

        return res

    def measure(self,split_pos=None):
        res=[]
        get_measure_prob(self)
        if split_pos==None:
            if self.key_2_index:
                split_pos=max(self.key_2_index)
            else:
                split_pos=self.node.key

        if split_pos==-1:
            return ''
        else:
            if split_pos!=self.node.key:
                l=random.randint(0,1)
                temp_res=self.measure(split_pos-1)
                res=str(l)+temp_res
                return res
            l=random.uniform(0,sum(self.node.meas_prob))
            if l<self.node.meas_prob[0]:
                temp_tdd=Slicing(self,self.node.key,0)
                temp_res=temp_tdd.measure(split_pos-1)
                res='0'+temp_res
            else:
                temp_tdd=Slicing(self,self.node.key,1)
                temp_res=temp_tdd.measure(split_pos-1)
                res='1'+temp_res
#         print(res)
        return res

    def get_amplitude(self,b):
        """b is the term for calculating the amplitude"""
        if len(b)==0:
            return self.weight.r.val+1j*self.weight.i.val
        
        if len(b)!=self.node.key+1:
            b.pop(0)
            return self.get_amplitude(b)
        else:
            temp_tdd=Slicing(self,self.node.key,b[0])
            b.pop(0)
            res=temp_tdd.get_amplitude(b)
            w=res*self.weight
            return w.r.val+1j*w.i.val
            
    def sampling(self,k):
        res=[]
        for k1 in range(k):
            temp_res=self.measure()
            res.append(temp_res )
#         print(res)
        return res
        
        
    def __eq__(self,other):
        if self.node==other.node and equals(self.weight,other.weight):# and self.key_2_index==other.key_2_index
            return True
        else:
            return False
        
def layout(node,key_2_idx,dot=None,succs=[],real_label=True):
    col=['red','blue','black','green']
    if real_label and node.key in key_2_idx:
        if node.key==-1:
            dot.node(str(node.idx), str(1), fontname="helvetica",shape="circle",color="red")
        else:
            dot.node(str(node.idx), key_2_idx[node.key], fontname="helvetica",shape="circle",color="red")
    else:
        dot.node(str(node.idx), str(node.key), fontname="helvetica",shape="circle",color="red")
    for k in range(node.succ_num):
        if node.succ[k]:
            label1=str(complex(round(node.succ[k].weight.r.val,2),round(node.succ[k].weight.i.val,2)))
            if not node.succ[k] in succs:
                dot=layout(node.succ[k].node,key_2_idx,dot,succs,real_label)
                dot.edge(str(node.idx),str(node.succ[k].node.idx),color=col[k%4],label=label1)
                succs.append(node.succ[k])
            else:
                dot.edge(str(node.idx),str(node.succ[k].node.idx),color=col[k%4],label=label1)
    return dot        

        
def Ini_TDD(index_order=[],max_rank=200):
    """To initialize the unique_table,computed_table and set up a global index order"""
    global unique_table,computed_table,terminal_node,global_node_idx,DDzero,DDone
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time

    global_node_idx=0
    
    unique_table = {k:dict() for k in range(max_rank)}
    
    computed_table = {'+': {k:{k1: dict() for k1 in range(-1,max_rank)} for k in range(-1,max_rank)},'*': {k:{k1: dict() for k1 in range(-1,max_rank)} for k in range(-1,max_rank)}}
    add_find_time=0
    add_hit_time=0
    cont_find_time=0
    cont_hit_time=0
    set_index_order(index_order)
    ini_complex(max_rank)
    terminal_node = Find_Or_Add_Unique_table(-1)
    DDzero = TDD(terminal_node,cn0)
    DDzero.index_2_key={-1:-1}
    DDzero.key_2_index={-1:-1}
    DDone = TDD(terminal_node,cn1)
    DDone.index_2_key={-1:-1}
    DDone.key_2_index={-1:-1}
    return DDone

def Clear_TDD():
    """To initialize the unique_table,computed_table and set up a global index order"""
    global computed_table
    global unique_table
    global global_node_idx
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time
    global_node_idx=0
    unique_table.clear()
    computed_table['+'].clear()
    computed_table['*'].clear()
    add_find_time=0
    add_hit_time=0
    cont_find_time=0
    cont_hit_time=0
    global_node_idx=0


def get_identity_tdd():
    return DDone

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
    return (int(round(weight.r.val/epi)) ,int(round(weight.i.val/epi)))

def get_node_set(node,node_set=set()):
    """Only been used when counting the node number of a TDD"""
    if not node in node_set:
        node_set.add(node)
        for k in range(node.succ_num):
            if node.succ[k]:
                node_set = get_node_set(node.succ[k].node,node_set)
    return node_set

def Find_Or_Add_Unique_table(x,the_successors=[]):
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
    temp_key = ((succ.weight.r,succ.weight.i,succ.node) for succ in the_successors)

    if temp_key in unique_table[x]:
        return unique_table[x][temp_key]
    else:
        res=Node(x,len(the_successors))
        global_node_idx+=1
        res.idx=global_node_idx
        res.succ = the_successors
        unique_table[x][temp_key] = res
    return res
    

def normalize(x,the_successors,cached = False):
    """The normalize and reduce procedure"""

    m = len(the_successors)
    
    all_equal=True
    for k in range(1,m):
        if the_successors[k]!=the_successors[0]:
            all_equal=False
            break        
    if all_equal:
        if not cached:
            return the_successors[0]
        if cached:
            for k in range(1,len(the_successors)):
                if the_successors[k].weight!=cn0 and the_successors[k].weight!=cn1:
                    releaseCached(the_successors[k].weight)
            return the_successors[0]
    
    is_zero=[equalsZero(the_successors[k].weight) for k in range(m)]
    if cached:
        for k in range(0,m):
            if is_zero[k] and the_successors[k].weight!=cn0:
                releaseCached(the_successors[k].weight)
                the_successors[k].weight = cn0
            
    
#     weigs_abs=[int(round(succ.weight.norm()/epi)) for succ in the_successors]
#     max_pos = weigs_abs.index(max(weigs_abs))
#     weig_max = the_successors[max_pos].weight
    
    max_pos = -1
    weig_max = cn1
    for k in range(m):
        if is_zero[k]: continue
        if max_pos == -1:
            max_pos = k
            weig_max = the_successors[k].weight
            weig_max_norm = weig_max.norm()
        else:
            mag = the_successors[k].weight.norm()
            if mag - weig_max_norm>epi:
                max_pos=k
                weig_max = the_successors[k].weight
                weig_max_norm = mag
    
    if max_pos == -1:
        return DDzero
            
    
    for k in range(m):
        if k==max_pos:
            if the_successors[k].weight!=cn1:
                the_successors[k].weight = cn1
        else:
            if the_successors[k].weight==cn0:
                continue
            if cached:
                if the_successors[k].weight!=cn1:
                    releaseCached(the_successors[k].weight)
                    the_successors[k].weight = Find_Or_Add_Complex_table(the_successors[k].weight/weig_max)
            elif equalsOne(weig_max):
                continue
            else:
                the_successors[k].weight = Find_Or_Add_Complex_table(the_successors[k].weight/weig_max)
    
    
    node = Find_Or_Add_Unique_table(x,the_successors)
    
    if cached:
        res=TDD(node,weig_max)
    else:
        if weig_max!=cn1:
            weig_max = Find_Or_Add_Complex_table(weig_max)
        res=TDD(node,weig_max)
        
#     print('526',x,res.weight,weigs[0],weigs[1])
    return res
              
              

def get_count():
    global add_find_time,add_hit_time,cont_find_time,cont_hit_time
    print("add:",add_hit_time,'/',add_find_time,'/',add_hit_time/add_find_time)
    print("cont:",cont_hit_time,"/",cont_find_time,"/",cont_hit_time/cont_find_time)

def find_computed_table(item):
    """To return the results that already exist"""
    global computed_table,add_find_time,add_hit_time,cont_find_time,cont_hit_time,add_hit_time2
    if item[0] == '+':
        key1=get_int_key(item[1].weight)
        key2=get_int_key(item[2].weight)
        the_key=(key1,item[1].node,key2,item[2].node)
        add_find_time+=1
        if computed_table['+'][item[1].node.key][item[2].node.key].__contains__(the_key):
            res = computed_table['+'][item[1].node.key][item[2].node.key][the_key]
            add_hit_time+=1
            if abs(res[0])<epi and abs(res[1])<epi:
                return TDD(terminal_node,cn0)
            else:
                tdd = TDD(res[2],getCachedComplex2(res[0],res[1]))
                return tdd
            
        the_key=(key2,item[2].node,key1,item[1].node)
        if computed_table['+'][item[2].node.key][item[1].node.key].__contains__(the_key):
            res = computed_table['+'][item[2].node.key][item[1].node.key][the_key]            
            add_hit_time+=1
            if abs(res[0])<epi and abs(res[1])<epi:
                return TDD(terminal_node,cn0)
            else:
                tdd = TDD(res[2],getCachedComplex2(res[0],res[1]))
                return tdd
    else:
        the_key=(item[1].node,item[2].node,item[3][0],item[3][1],item[4])
        cont_find_time+=1
        if computed_table['*'][item[1].node.key][item[2].node.key].__contains__(the_key):
            res = computed_table['*'][item[1].node.key][item[2].node.key][the_key]
            cont_hit_time+=1
            if abs(res[0])<epi and abs(res[1])<epi:
                return TDD(terminal_node,cn0)
            else:
                tdd = TDD(res[2],getCachedComplex2(res[0],res[1]))
                return tdd
        the_key=(item[2].node,item[1].node,item[3][1],item[3][0],item[4])
        if computed_table['*'][item[2].node.key][item[1].node.key].__contains__(the_key):
            cont_hit_time+=1
            res = computed_table['*'][item[2].node.key][item[1].node.key][the_key]
            if abs(res[0])<epi and abs(res[1])<epi:
                return TDD(terminal_node,cn0)
            else:
                tdd = TDD(res[2],getCachedComplex2(res[0],res[1]))
                return tdd
    return None

def insert_2_computed_table(item,res):
    """To insert an item to the computed table"""
    global computed_table,cont_time,find_time,hit_time

    if item[0] == '+':
        key1=get_int_key(item[1].weight)
        key2=get_int_key(item[2].weight)        
        the_key = (key1,item[1].node,key2,item[2].node)
        computed_table['+'][item[1].node.key][item[2].node.key][the_key] = (res.weight.r.val,res.weight.i.val,res.node)
    else:
        the_key = (item[1].node,item[2].node,item[3][0],item[3][1],item[4])
        computed_table['*'][item[1].node.key][item[2].node.key][the_key] = (res.weight.r.val,res.weight.i.val,res.node)
    
def get_index_2_key(var):
    var_sort=copy.copy(var)
    var_sort.sort()
    var_sort.reverse()
    idx_2_key={-1:-1}
    key_2_idx={-1:-1}
    n=0
    for idx in var_sort:
        if not idx.key in idx_2_key:
            idx_2_key[idx.key]=n
            key_2_idx[n]=idx.key
            n+=1
    return idx_2_key,key_2_idx
    
def get_tdd(U,var=[]):
    
#     if len(var)==0 or not isinstance(var[0],Index):
#         return np_2_tdd(U,var)
    
    idx_2_key, key_2_idx = get_index_2_key(var)
    order=[]
    for idx in var:
        order.append(idx_2_key[idx.key])
        
    tdd = np_2_tdd(U,order)
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
    tdd.index_set=var
    
#     if not order:
#         order=list(range(U_dim))
        
#     for k in range(max(order)+1):
#         split_pos=order.index(k)
#         tdd.key_width[k]=U.shape[split_pos]
        
    return tdd    
    
def get_tdd2(U,var,idx_2_key=None):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    if sum(U.shape)==U_dim:
        for k in range(U_dim):
            U=U[0]
        res=TDD(terminal_node,Find_Or_Add_Complex_table(getTempCachedComplex2(U)))
        return res
     
    if not idx_2_key:
        idx_2_key = get_index_2_key(var)
        
    min_index=min(var)
    x=min_index.key
    min_pos=var.index(min_index)
#     print(min_pos)
    new_var=copy.copy(var)
    new_var[min_pos]=Index(-1)
    split_U=np.split(U,2,min_pos)
    new_var_key=[idx.key for idx in new_var]
    
    while x in new_var_key:
        min_pos=new_var_key.index(x)
        split_U[0]=np.split(split_U[0],2,min_pos)[0]
        split_U[1]=np.split(split_U[1],2,min_pos)[1]
        new_var[min_pos]=Index(-1)
        new_var_key[min_pos]=-1
        
    low=get_tdd(split_U[0],new_var,idx_2_key)
    high=get_tdd(split_U[1],new_var,idx_2_key)
    tdd = normalize(idx_2_key[x], [low,high])
    for k in range(len(idx_2_key)):
        tdd.key_width[k]=2
    tdd.index_2_key=idx_2_key
    key_2_idx=dict()
    for k in idx_2_key:
        key_2_idx[idx_2_key[k]]=k
    tdd.key_2_index=key_2_idx
    return tdd

def np_2_tdd(U,order=[],key_width=True):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    U_shape=U.shape
    if sum(U_shape)==U_dim:
        
        for k in range(U_dim):
            U=U[0]
        res=TDD(terminal_node,Find_Or_Add_Complex_table(getTempCachedComplex2(U)))
        return res
    
    if not order:
        order=list(range(U_dim))
    
    if key_width:
        the_width=dict()
        for k in range(max(order)+1):
            split_pos=order.index(k)
            the_width[k]=U.shape[split_pos]
            
    x=max(order)
    split_pos=order.index(x)
    order[split_pos]=-1
    split_U=np.split(U,U_shape[split_pos],split_pos)
    
    while x in order:
        split_pos=order.index(x)
        for k in range(len(split_U)):
            split_U[k]=np.split(split_U[k],U_shape[split_pos],split_pos)[k]
        order[split_pos]=-1
    
    the_successors=[]
    for k in range(U_shape[split_pos]):
        res=np_2_tdd(split_U[k],copy.copy(order),False)
        the_successors.append(res)
    tdd = normalize(x,the_successors)
    
    if key_width:
        tdd.key_width=the_width
    
    return tdd
    
    
def np_2_tdd2(U,split_pos=None):
    #index is the index_set as the axis order of the matrix
    U_dim=U.ndim
    U_shape=U.shape
    if sum(U_shape)==U_dim:
        for k in range(U_dim):
            U=U[0]
        res=TDD(terminal_node,Find_Or_Add_Complex_table(getTempCachedComplex2(U)))
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
    
def tdd_2_np(tdd,split_pos=None,key_repeat_num=dict()):
#     print(split_pos,key_repeat_num)
    if split_pos==None:
        split_pos=tdd.node.key
            
    if split_pos==-1:
        return tdd.weight.r.val+1j*tdd.weight.i.val
    else:
        the_succs=[]
        for k in range(tdd.key_width[split_pos]):
            succ=Slicing2(tdd,split_pos,k)
            succ.key_width=tdd.key_width
            temp_res=tdd_2_np(succ,split_pos-1,key_repeat_num)
            the_succs.append(temp_res)
        if not split_pos in key_repeat_num:
            r = 1
        else:
            r = key_repeat_num[split_pos]
            
        if r==1:
            res=np.stack(tuple(the_succs), axis=the_succs[0].ndim)
        else:
            new_shape=list(the_succs[0].shape)
            for k in range(r):
                new_shape.append(tdd.key_width[split_pos])
            res=np.zeros(new_shape)
            for k1 in range(tdd.key_width[split_pos]):
                f='res['
#                 print(the_succs[0].ndim,r-1)
                for k2 in range(the_succs[0].ndim):
                    f+=':,'
                for k3 in range(r-1):
                    f+=str(k1)+','
                f=f[:-1]+']'
                eval(f)[k1]=the_succs[k1]
        return res
    
    
"""need modify"""                
def get_measure_prob(tdd):
    if tdd.node.meas_prob:
        return tdd
    if tdd.node.key==-1:
        tdd.node.meas_prob=[0.5,0.5]
        return tdd
    if not tdd.node.succ_num==2:
        print("Only can be used for binary quantum state")
        return tdd
    get_measure_prob(Slicing(tdd,tdd.node.key,0))
    get_measure_prob(Slicing(tdd,tdd.node.key,1))
    tdd.node.meas_prob=[0]*2
    p0=tdd.node.out_weight[0].r.val*tdd.node.out_weight[0].r.val+tdd.node.out_weight[0].i.val*tdd.node.out_weight[0].i.val
    p1=tdd.node.out_weight[1].r.val*tdd.node.out_weight[1].r.val+tdd.node.out_weight[1].i.val*tdd.node.out_weight[1].i.val
                
    tdd.node.meas_prob[0]=p0*sum(tdd.node.succ[0].node.meas_prob)*2**(tdd.node.key-tdd.node.succ[0].node.key-1)
    tdd.node.meas_prob[1]=p1*sum(tdd.node.succe[1].node.meas_prob)*2**(tdd.node.key-tdd.node.succ[1].node.key-1)
    return tdd

    
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
    
#     print('857 in cacheCount',cacheCount)
    cacheCount_in=cacheCount
    tdd=contract(tdd1,tdd2,key_2_new_key,cont_order,len(set(var_cont_idx)))
    if not tdd.weight==cn0 and not tdd.weight==cn1:
        releaseCached(tdd.weight)
    tdd.weight=Find_Or_Add_Complex_table(tdd.weight)
#     print('862 out cacheCount',cacheCount)
    if not cacheCount==cacheCount_in:
        print('Something went wrong, cacheCount not match')
    
    tdd.index_set=var_out
    tdd.index_2_key=idx_2_key
    tdd.key_2_index=key_2_idx
    key_width=dict()
    for k1 in range(len(key_2_new_key[0])):
        if not key_2_new_key[0][k1]=='c' and not key_2_new_key[0][k1] ==-1:
            key_width[key_2_new_key[0][k1]]=tdd1.key_width[k1]
    for k2 in range(len(key_2_new_key[1])):
        if not key_2_new_key[1][k2]=='c' and not key_2_new_key[1][k2] ==-1:
            key_width[key_2_new_key[1][k2]]=tdd2.key_width[k2]             
   
    tdd.key_width=key_width
#     print(tdd1.key_width,tdd2.key_width,tdd.key_width)
    return tdd
    

def contract(tdd1,tdd2,key_2_new_key,cont_order,cont_num):
    """The contraction of two TDDs, var_cont is in the form [[4,1],[3,2]]"""

    k1=tdd1.node.key
    k2=tdd2.node.key
    w1=tdd1.weight
    w2=tdd2.weight
#     print('930',k1,k2,w1,w2)
    if w1== cn0 or w2==cn0:
        return DDzero    
    
    if k1==-1 and k2==-1:
        tdd=TDD(terminal_node,cn_mulCached(w1,w2))
        if cont_num>0:
            temp = getTempCachedComplex2(2**cont_num)
            cn_mul(tdd.weight,tdd.weight,temp)
        return tdd

    if k1==-1:
        if cont_num ==0 and key_2_new_key[1][k2]==k2:
            tdd=TDD(tdd2.node,cn_mulCached(w1,w2))
            return tdd
            
    if k2==-1:      
        if cont_num ==0 and key_2_new_key[0][k1]==k1:
            tdd=TDD(tdd1.node,cn_mulCached(w1,w2))
            return tdd
    
    tdd1.weight = cn1
    tdd2.weight = cn1

    temp_key_2_new_key=[]
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[0][:(k1+1)]]))
    temp_key_2_new_key.append(tuple([k for k in key_2_new_key[1][:(k2+1)]]))
    
    tdd = find_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num])
    if tdd:
        tdd1.weight=w1
        tdd2.weight=w2
        if not tdd.weight==cn0:
            cn_mul(tdd.weight,tdd.weight,w1)
            cn_mul(tdd.weight,tdd.weight,w2)
            if equalsZero(tdd.weight):
                releaseCached(tdd.weight)
                return DDzero
        return tdd
                
    if cont_order[0][k1]<cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors,True)
        else:
            tdd=DDzero
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),tdd2,key_2_new_key,cont_order,cont_num-1)
                if tdd.weight==cn0:
                    tdd=res
                elif res.weight != cn0:
                    old_w = tdd.weight
                    tdd=add(tdd,res)
                    releaseCached(old_w)
                    releaseCached(res.weight)
                    
    elif cont_order[0][k1]==cont_order[1][k2]:
        the_key=key_2_new_key[0][k1]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors,True)
        else:
            tdd=DDzero
            for k in range(tdd1.node.succ_num):
                res=contract(Slicing(tdd1,k1,k),Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                if tdd.weight==cn0:
                    tdd=res
                elif res.weight != cn0:
                    old_w = tdd.weight
                    tdd=add(tdd,res)
                    releaseCached(old_w)
                    releaseCached(res.weight)
    else:
        the_key=key_2_new_key[1][k2]
        if the_key!='c':
            the_successors=[]
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num)
                the_successors.append(res)
            tdd=normalize(the_key,the_successors,True)
        else:
            tdd=DDzero
            for k in range(tdd2.node.succ_num):
                res=contract(tdd1,Slicing(tdd2,k2,k),key_2_new_key,cont_order,cont_num-1)           
                if tdd.weight==cn0:
                    tdd=res
                elif res.weight != cn0:
                    old_w = tdd.weight
                    tdd=add(tdd,res)
                    releaseCached(old_w)
                    releaseCached(res.weight)
                    
    insert_2_computed_table(['*',tdd1,tdd2,temp_key_2_new_key,cont_num],tdd)
    tdd1.weight=w1
    tdd2.weight=w2
    if not tdd.weight==cn0 and (w1!=cn1 or w2!=cn1):
        if tdd.weight==cn1:
            tdd.weight = cn_mulCached(w1,w2)
        else:
            cn_mul(tdd.weight,tdd.weight,w1)
            cn_mul(tdd.weight,tdd.weight,w2)
        if equalsZero(tdd.weight):
            releaseCached(tdd.weight)
            return DDzero
    return tdd
    
def Slicing(tdd,x,c):
    """Slice a TDD with respect to x=c"""

    if tdd.node.key==x:
        return tdd.node.succ[c]
    
    if tdd.node.key==-1:
        return tdd
    
    if tdd.node.key<x:
        return tdd   
    else:
        print("Not supported yet!!!")
        
        
def Slicing2(tdd,x,c):
    """Slice a TDD with respect to x=c"""

    if tdd.node.key==x:
        if tdd.node.succ[c].weight == cn0:
            return DDzero
        else:
            res=TDD(tdd.node.succ[c].node,cn_mulCached(tdd.node.succ[c].weight,tdd.weight))
            return res
    
    if tdd.node.key==-1:
        return tdd
    
    if tdd.node.key<x:
        return tdd
    else:
        print("Not supported yet!!!")        
        
        

def add(tdd1,tdd2):

    k1=tdd1.node.key
    k2=tdd2.node.key
#     print('add 1078',k1,k2,tdd1.weight,tdd2.weight)
    if tdd1.weight==cn0:
        if tdd2.weight==cn0:
            return DDzero
        else:
#             tdd2.weight=getCachedComplex2(tdd2.weight.r.val,tdd2.weight.i.val)
#             return tdd2
            res = TDD(tdd2.node,getCachedComplex2(tdd2.weight.r.val,tdd2.weight.i.val))
            return res 
    
    if tdd2.weight == cn0:
#         tdd1.weight = getCachedComplex2(tdd1.weight.r.val,tdd1.weight.i.val)
#         return tdd1
        res = TDD(tdd1.node,getCachedComplex2(tdd1.weight.r.val,tdd1.weight.i.val))
        return res
    
    if tdd1.node==tdd2.node:
        weig=cn_addCached(tdd1.weight,tdd2.weight)
        if equalsZero(weig):
            releaseCached(weig)
            return DDzero
        else:
            res=TDD(tdd1.node,weig)
            return res
        
    res = find_computed_table(['+',tdd1,tdd2])
    if res:
        return res
    
    the_successors=[]
    if k1>k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            e1 = Slicing2(tdd1,x,k)
            e2 = tdd2
            res=add(e1,e2)
            the_successors.append(res)
            if not e1.weight==cn0:
                releaseCached(e1.weight)
    elif k1==k2:
        x=k1
        for k in range(tdd1.node.succ_num):
            e1=Slicing2(tdd1,x,k)
            e2=Slicing2(tdd2,x,k)
            res=add(e1,e2)
            the_successors.append(res)
            if not e1.weight==cn0:
                releaseCached(e1.weight)
            if not e2.weight==cn0:
                releaseCached(e2.weight)              
    else:
        x=k2
        for k in range(tdd2.node.succ_num):
            e1=tdd1
            e2=Slicing2(tdd2,x,k)
            res=add(e1,e2)
            the_successors.append(res)
            if not e2.weight==cn0:
                releaseCached(e2.weight)
                
    res = normalize(x,the_successors,True)
    insert_2_computed_table(['+',tdd1,tdd2],res)
    return res


def incRef(tdd):
    if tdd.node.key==-1:
        return
    
    tdd.node.ref_num+=1
    
    if tdd.node.ref_num==1:
        for k in range(tdd1.node.succ_num):
            incRef(Slicing(tdd,tdd.node.key,k))
            
def decRef(tdd):
    if tdd.node.key==-1:
        return
    
    if tdd.node.ref_num==1:
        print('Error In defRef')
    
    tdd.node.ref_num-=1
    
    if tdd.node.ref_num==0:
        for k in range(tdd1.node.succ_num):
            decRef(Slicing(tdd,tdd.node.key,k))            
    
    

def garbageCollect():
    global computed_table
    global unique_table
    temp_unique_table = dict()
    for item in unique_table:
        if not unique_table[item].ref_num==0:
            temp_unique_table[item] = unique_table[item]
    
    unique_table.clear()
    
    unique_table = temp_unique_table              
