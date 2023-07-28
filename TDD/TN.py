import numpy as np
from TDD.TDD import Index,get_tdd,get_identity_tdd,cont
import networkx as nx
from networkx.algorithms.approximation.treewidth import treewidth_min_degree,treewidth_min_fill_in

common_tensor_table = dict()

class Tensor:
    def __init__(self,data=[],index=[],name=None,qubits=None):
        self.data=data
        self.index_set=index
        self.name=name
        self.qubits=qubits #This is used only when it represent a quantum gate 
        
    def tdd(self):
        return get_tdd(self.data,self.index_set)        
        
class TensorNetwork:
    def __init__(self,tensors=dict(),tn_type='tn',qubits_num=0):
        self.tensors=tensors
        self.tn_type=tn_type
        self.index_set=set()
        self.index_2_tensor=dict()
        self.qubits_num=qubits_num #This is used only when it represent a quantum circuit
#         if len(data)>0 and len(index_set)==0:
#             self.index_set=self.get_index_set()
#         if len(data)>0 and len(index_2_node)==0:
#             self.index_2_node=self.get_index_2_node()
    def cont(self,optimizer=None):
        tdd=get_identity_tdd()        
        if optimizer=='tree_decomposition':
            decom_tree,tree_width=get_tree_decomposition(self)
            cont_index = find_contraction_index(decom_tree)
            computed_tdd_list=[]
            while cont_index:
                computed_tdd_list = contract_an_index(self,cont_index,computed_tdd_list)
                cont_index=find_contraction_index(decom_tree)
            
            for temp_tdd in computed_tdd_list:
                tdd=cont(tdd,temp_tdd)
            return tdd
        if optimizer=='cir_partition1':
            if not self.tn_type=='cir':
                print("This optimizer is only used for quantum circuits!")
                return tdd
            partion_cir=circuit_partion1(self)
            for level in range(len(partion_cir)):
                temp_tn=TensorNetwork(partion_cir[level][0])
                tdd1=temp_tn.cont()
                temp_tn=TensorNetwork(partion_cir[level][1])
                tdd2=temp_tn.cont()              
                temp_tdd=cont(tdd1,tdd2)
                tdd=cont(tdd,temp_tdd)
            return tdd
        
        if optimizer=='cir_partition2':
            if not self.tn_type=='cir':
                print("This optimizer is only used for quantum circuits!")
                return tdd
            partion_cir=circuit_partion2(self)
            
            for level in range(len(partion_cir)):
                temp_tn=TensorNetwork(partion_cir[level][0])
                tdd1=temp_tn.cont()
                temp_tn=TensorNetwork(partion_cir[level][1])
                tdd2=temp_tn.cont()
                temp_tdd=cont(tdd1,tdd2)
                temp_tn=TensorNetwork(partion_cir[level][2])
                tdd3=temp_tn.cont()            
                temp_tdd=cont(tdd3,temp_tdd)
                tdd=cont(tdd,temp_tdd)
            return tdd        
        
        for ts in self.tensors:
            temp_tdd=ts.tdd()
            tdd=cont(tdd,temp_tdd)
        return tdd

    def get_index_set(self):
        for ts in self.tensors:
            temp_index=[idx.key for idx in ts.index_set]
            for idx in temp_index:
                self.index_set.add(idx)
                if not idx in self.index_2_tensor:
                    self.index_2_tensor[idx]=set()
                self.index_2_tensor[idx].add(ts)

    
#     def get_index_2_node(self):
#         index_2_node=dict()
#         for k in range(len(data)):
#             temp_index=[idx.key for idx in self.data[k].index]
#             for idx in temp_index:
#                 if not idx in index_2_node:
#                     index_2_node[idx]=set()
#                 index_2_node[idx].add(k)
#         return index_2_node
    
    
def get_tree_decomposition(tn):
    lin_graph=nx.Graph()
    if not tn.index_set:
        tn.get_index_set()
    
    lin_graph.add_nodes_from(tn.index_set)
    
    for ts in tn.tensors:    
        for k1 in range(len(ts.index_set)):
            for k2 in range(k1+1,len(ts.index_set)):
                if ts.index_set[k1].key!=ts.index_set[k2].key:
                    lin_graph.add_edge(ts.index_set[k1].key,ts.index_set[k2].key)
        
    tree_width,de_graph=treewidth_min_fill_in(lin_graph)
#     print('The treewidth is',tree_width)
    return de_graph,tree_width

def find_contraction_index(tree_decomposition):
    idx=None
    if len(tree_decomposition.nodes)==1:
        nod=[k for k in tree_decomposition.nodes][0]
        if len(nod)!=0:
            idx=[idx for idx in nod][0]
            nod_temp=set(nod)
            nod_temp.remove(idx)
            tree_decomposition.add_node(frozenset(nod_temp))
            tree_decomposition.remove_node(nod)
        return idx
    nod=0
    for k in tree_decomposition.nodes:
        if nx.degree(tree_decomposition)[k]==1:
            nod=k
            break
            
    neib=[k for k in tree_decomposition.neighbors(nod)][0]
    for k in nod:
        if not k in neib:
            idx=k
            break
    if idx:     
        nod_temp=set(nod)
        nod_temp.remove(idx)
        tree_decomposition.remove_node(nod)
        if frozenset(nod_temp)!=neib:
            tree_decomposition.add_node(frozenset(nod_temp))
            tree_decomposition.add_edge(frozenset(nod_temp),neib)
        return idx
    else:
        tree_decomposition.remove_node(nod)
        return find_contraction_index(tree_decomposition)

    
def contract_an_index(tn,cont_index,computed_tdd_list):
    temp_tn=TensorNetwork(tn.index_2_tensor[cont_index])
    temp_tdd=temp_tn.cont()
    
    for ts in tn.index_2_tensor[cont_index]:
        for idx in ts.index_set:
            if idx.key!=cont_index:
                if ts in tn.index_2_tensor[idx.key]:
                    tn.index_2_tensor[idx.key].remove(ts)
    temp_computed_tdd_list = []
    for tdd in computed_tdd_list:
        tdd_idx_out=[k.key for k in tdd.index_set]

        if cont_index in tdd_idx_out:
            temp_tdd=cont(tdd,temp_tdd)
        else:
            temp_computed_tdd_list.append(tdd)
    temp_computed_tdd_list.append(temp_tdd)
    computed_tdd_list = temp_computed_tdd_list
    return computed_tdd_list            
            
def circuit_partion1(tn):
    """The first partition scheme; 
    cx_max is the number of CNOTs allowed to be cut
    """
    res=[[[],[]]]
    
    num_qubit=tn.qubits_num
    
    cx_max=num_qubit//2
    cx_num=0
    level=0
        
    qubits = []    
    qubits.append([k for k in range(num_qubit//2)])
    qubits.append([k for k in range(num_qubit//2,num_qubit)])

    for ts in tn.tensors:
        q = ts.qubits
        if max(q) in qubits[0]:
            res[level][0].append(ts)
        elif min(q) in qubits[1]:
            res[level][1].append(ts)
        else:
            cx_num+=1
            if cx_num<=cx_max:
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
            else:
                level+=1
                res.append([])
                res[level].append([])
                res[level].append([])
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
                cx_num=1
                
#     print('circuit blocks:',2*(level+1))
    return res            
            
def circuit_partion2(tn):
    """The first partition scheme; 
    cx_max is the number of CNOTs allowed to be cut
    """
    res=[[[],[],[]]]
    
    cx_num=0
    num_qubit=tn.qubits_num
    cx_max = num_qubit//2
    c_part_width = num_qubit//2+1
    level=0
    
    qubits=[]
    qubits.append([k for k in range(num_qubit//2)])
    qubits.append([k for k in range(num_qubit//2,num_qubit)])
    qubits.append([])
    c_range=[num_qubit,0]
    
    for ts in tn.tensors:
        q = ts.qubits
        
        
        if max(q) in qubits[0]:
            res[level][0].append(ts)
        elif min(q) in qubits[1]:
            res[level][1].append(ts)
        elif min(q) in qubits[2] and max(q) in qubits[2]:        
            res[level][2].append(ts)
        else:
            if cx_num < cx_max:
                cx_num+=1
                if q[-1] in qubits[0]:
                    res[level][0].append(ts)
                else:
                    res[level][1].append(ts)
            else:
                c_width = max(c_range[1],max(q))-min(c_range[0],min(q))+1
                if c_width < c_part_width:
                    res[level][2].append(ts)
                    c_range[0]=min(c_range[0],min(q))
                    c_range[1]=max(c_range[1],max(q))
                    qubits[0]=[k for k in range(0,c_range[0])]
                    qubits[1]=[k for k in range(c_range[1]+1,num_qubit)]
                    qubits[2]=[k for k in range(c_range[0],c_range[1]+1)]
                else:
                    level+=1
                    res.append([])
                    res[level].append([])
                    res[level].append([])
                    res[level].append([])
                    qubits.clear()
                    qubits.append([k for k in range(num_qubit//2)])
                    qubits.append([k for k in range(num_qubit//2,num_qubit)])
                    qubits.append([])
                    c_range=[num_qubit,0]
                    
                    if max(q) in qubits[0]:
                        res[level][0].append(ts)
                        cx_num=0
                    elif min(q) in qubits[1]:
                        res[level][1].append(ts)
                        cx_num=0
                    else:
                        if q[-1] in qubits[0]:
                            res[level][0].append(ts)
                        else:
                            res[level][1].append(ts)
                        cx_num=1
            
#     print('circuit blocks:',3*(level+1))
    return res