import numpy as np
from TDD.TN import Index,Tensor,TensorNetwork
from qiskit.quantum_info.operators import Operator
import time

def is_diagonal(U):
    i, j = np.nonzero(U)
    return np.all(i == j)

def add_hyper_index(var_list,hyper_index):
    for var in var_list:
        if not var in hyper_index:
            hyper_index[var]=0
            
def reshape(U):
    if U.shape==(2,2):
        return U
    
    if U.shape[0]==U.shape[1]:
        split_U=np.split(U,2,1)
    else:
        split_U=np.split(U,2,0)
    split_U[0]=reshape(split_U[0])
    split_U[1]=reshape(split_U[1]) 
    return np.array([split_U])[0]            
            
def get_real_qubit_num(cir):
    """Calculate the real number of qubits of a circuit"""
    gates=cir.data
    q=0
    for k in range(len(gates)):
        q=max(q,max([qbit.index for qbit in gates[k][1]]))
    return q+1

def cir_2_tn(cir,input_s=[],output_s=[]):
    """return the dict that link every quantum gate to the corresponding index"""
#     print(1)
#     t=time.time()
    
    
    hyper_index=dict()
    qubits_index = dict()
    start_tensors= dict()
    end_tensors = dict()
    
    qubits_num=get_real_qubit_num(cir)

    for k in range(qubits_num):
        qubits_index[k]=0
        
    tn=TensorNetwork([],tn_type='cir',qubits_num=qubits_num)

        
    if input_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('x'+str(k))],'in',[k])
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('x'+str(k))],'in',[k])
            else:
                print('Only support computational basis input')
            tn.tensors.append(ts)
                
    gates=cir.data
    for k in range(len(gates)):
        g=gates[k]
        nam=g[0].name
        q = [q.index for q in g[1]]
        var=[]
        if nam=='cx':
#             print(Operator(g[0]).data)
            var_con='x'+ str(q[0])+'_'+str(qubits_index[q[0]])
            var_tar_in='x'+ str(q[1])+'_'+str(qubits_index[q[1]])
            var_tar_out='x'+ str(q[1])+'_'+str(qubits_index[q[1]]+1)
            add_hyper_index([var_con,var_tar_in,var_tar_out],hyper_index)
            var+=[Index(var_con,hyper_index[var_con]),Index(var_con,hyper_index[var_con]+1),Index(var_tar_in,hyper_index[var_tar_in]),Index(var_tar_out,hyper_index[var_tar_out])]
            U=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
            U=reshape(U)
            ts=Tensor(U,var,nam,q)
            tn.tensors.append(ts)
            if qubits_index[q[0]]==0 and hyper_index[var_con]==0:
                start_tensors[q[0]]=ts
            if qubits_index[q[1]]==0 and hyper_index[var_tar_in]==0:
                start_tensors[q[1]]=ts
            end_tensors[q[0]]=ts
            end_tensors[q[1]]=ts
            hyper_index[var_con]+=1
            qubits_index[q[1]]+=1            
            continue
        ts=Tensor([],[],nam,q)
        U=Operator(g[0]).data
        if is_diagonal(U):
            for k in q:
                var_in='x'+ str(k)+'_'+str(qubits_index[k])
                add_hyper_index([var_in],hyper_index)
                var+=[Index(var_in,hyper_index[var_in]),Index(var_in,hyper_index[var_in]+1)]
                if qubits_index[k]==0 and hyper_index[var_in]==0:
                    start_tensors[k]=ts
                end_tensors[k]=ts             
                hyper_index[var_in]+=1
        else:
            for k in q:
                var_in='x'+ str(k)+'_'+str(qubits_index[k])
                var_out='x'+ str(k)+'_'+str(qubits_index[k]+1)
                add_hyper_index([var_in,var_out],hyper_index)
                var+=[Index(var_in,hyper_index[var_in]),Index(var_out,hyper_index[var_out])]
                if qubits_index[k]==0 and hyper_index[var_in]==0:
                    start_tensors[k]=ts
                end_tensors[k]=ts                
                qubits_index[k]+=1
        if len(q)>1:
            U=reshape(U)
        ts.data=U
        ts.index_set=var
        tn.tensors.append(ts)

#     print(2)
#     print(time.time()-t)           

    for k in range(qubits_num):
        if k in start_tensors:
            last1=Index('x'+str(k)+'_'+str(0),0)
            new1=Index('x'+str(k),0)            
            start_tensors[k].index_set[start_tensors[k].index_set.index(last1)]=new1
        if k in end_tensors:
            last2=Index('x'+str(k)+'_'+str(qubits_index[k]),hyper_index['x'+str(k)+'_'+str(qubits_index[k])])
            new2=Index('y'+str(k),0)            
            end_tensors[k].index_set[end_tensors[k].index_set.index(last2)]=new2
               
    for k in range(qubits_num):
        U=np.eye(2)
        if qubits_index[k]==0 and not 'x'+str(k)+'_'+str(0) in hyper_index:
            var_in='x'+str(k)
            var=[Index('x'+str(k),0),Index('y'+str(k),0)]
            ts=Tensor(U,var,'nu_q',[k])
            tn.tensors.append(ts)            
#     print(3)
#     print(time.time()-t)
    if output_s:
        U0=np.array([1,0])
        U1=np.array([0,1])
        for k in range(qubits_num):
            if input_s[k]==0:
                ts=Tensor(U0,[Index('y'+str(k))],'out',[k])
            elif input_s[k]==1:
                ts=Tensor(U1,[Index('y'+str(k))],'out',[k])
            else:
                print('Only support computational basis output')
            tn.tensors.append(ts)
    
    all_indexs=[]
    for k in range(qubits_num):
        all_indexs.append('x'+str(k))
        for k1 in range(qubits_index[k]+1):
            all_indexs.append('x'+str(k)+'_'+str(k1))
        all_indexs.append('y'+str(k))
#     print(4)
#     print(time.time()-t)
    return tn,all_indexs

def add_inputs(tn,input_s,qubits_num):
    U0=np.array([1,0])
    U1=np.array([0,1])
    if len(input_s)!= qubits_num:
        print("inputs is not match qubits number")
        return 
    for k in range(qubits_num-1,-1,-1):
        if input_s[k]==0:
            ts=Tensor(U0,[Index('x'+str(k))],'in',[k])
        elif input_s[k]==1:
            ts=Tensor(U1,[Index('x'+str(k))],'in',[k])
        else:
            print('Only support computational basis input')
        tn.tensors.insert(0,ts)
            
def add_outputs(tn,output_s,qubits_num):
    U0=np.array([1,0])
    U1=np.array([0,1])
    if len(output_s)!= qubits_num:
        print("outputs is not match qubits number")
        return 
    for k in range(qubits_num):
        if output_s[k]==0:
            ts=Tensor(U0,[Index('y'+str(k))],'out',[k])
        elif output_s[k]==1:
            ts=Tensor(U1,[Index('y'+str(k))],'out',[k])
        else:
            print('Only support computational basis output')
        tn.tensors.append(ts)       

def add_trace_line(tn,qubits_num):
    U=np.eye(2)
    for k in range(qubits_num-1,-1,-1):
        var_in='x'+str(k)
        var=[Index('x'+str(k),0),Index('y'+str(k),0)]
        ts=Tensor(U,var,'tr',[k])
        tn.tensors.insert(0,ts)
        
# def Single_qubit_gate_2TDD(U,var):
#     """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
#     idx_2_key={-1:-1}
#     key_2_idx={-1:-1}
#     if var[0]<var[1]:
#         idx_2_key[var[0].key]=1
#         idx_2_key[var[1].key]=0
#         key_2_idx[0]=var[1].key
#         key_2_idx[1]=var[0].key
#     else:
#         idx_2_key[var[0].key]=0
#         idx_2_key[var[1].key]=1
#         key_2_idx[0]=var[0].key
#         key_2_idx[1]=var[1].key 
    
#     res=get_tdd(U,[var[1],var[0]],idx_2_key) 
#     res.index_set=var
#     res.index_2_key=idx_2_key
#     res.key_2_index=key_2_idx
#     return res 

# def diag_matrix_2_TDD(U,var):
#     term=Find_Or_Add_Unique_table(-1)
#     if get_int_key(U[0][0])==get_int_key(U[1][1]):
#         res=TDD(term)
#         res.weight=U[0][0]
#     else:
#         low=TDD(term)
#         low.weight=U[0][0]
#         high=TDD(term)
#         high.weight=U[1][1]
#         res=normalize(0, [low, high])
#     res.index_set=var
#     res.index_2_key={-1:-1,var[0].key:0}
#     res.key_2_index={-1:-1,0:var[0].key}
#     res.key_width[0]=2
#     return res

# def diag_matrix_2_TDD2(U,var):
#     if var[0]<var[2]:
#         x1=var[0].key
#         x0=var[2].key
#         low = diag_matrix_2_TDD(U[:2,:2],var[2:])
#         high = diag_matrix_2_TDD(U[2:,2:],var[2:])          
#     else:
#         x1=var[2].key
#         x0=var[0].key
#         low = diag_matrix_2_TDD(np.diag([U[0][0],U[2,2]]),var[:2])
#         high = diag_matrix_2_TDD(np.diag([U[1][1],U[3,3]]),var[:2])
       
    
#     if low==high:
#         res=low
#     else:
#         res=normalize(1,[low,high])
        
#     res.index_set=var
#     res.index_2_key={-1:-1,x0:0,x1:1}
#     res.key_2_index={-1:-1,0:x0,1:x1}
#     res.key_width[0]=res.key_width[1]=2
#     return res


# def cnot_2_TDD(var,case=1):
    
#     if case==2:
#         term=Find_Or_Add_Unique_table(-1)
#         res=TDD(term)
#         res.index_set = [var[0],var[1],var[2]]
#         res.index_2_key={-1:-1,var[0].key:0}
#         res.key_2_index={-1:-1,0:var[0].key}
#         return res
#     XOR=np.zeros((2,2,2))
#     XOR[0][0][0]=XOR[0][1][1]=XOR[1][0][1]=XOR[1][1][0]=1
    
#     idx_2_key={-1:-1}
#     key_2_idx={-1:-1}
    
#     new_var=[var[0],var[3],var[4]]
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=0
#     key_2_idx[0]=max_var.key
#     new_var.remove(max_var)
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=1
#     key_2_idx[1]=max_var.key
#     new_var.remove(max_var)
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=2
#     key_2_idx[2]=max_var.key
#     res=get_tdd(XOR,[var[0],var[3],var[4]],idx_2_key)
#     res.index_2_key=idx_2_key
#     res.key_2_index=key_2_idx
#     if case==1:
#         res.index_set=[var[0],var[2],var[3],var[4]]
#     else:
#         res.index_set=[var[1],var[3],var[4]]
#     res.key_width[0]=res.key_width[1]=res.key_width[2]=2
#     return res

# def Two_qubit_gate_2TDD(U,var):
#     """Get the TDD of a 2*2 matrix, here var = [column index, row index]"""
#     U=U.reshape(2,2,2,2)
#     idx_2_key={-1:-1}
#     key_2_idx={-1:-1}
    
#     new_var=[var[0],var[1],var[2],var[3]]
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=0
#     key_2_idx[0]=max_var.key
#     new_var.remove(max_var)
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=1
#     key_2_idx[1]=max_var.key
#     new_var.remove(max_var)
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=2
#     key_2_idx[2]=max_var.key
#     new_var.remove(max_var)
#     max_var=max(new_var)
#     idx_2_key[max_var.key]=3
#     key_2_idx[3]=max_var.key
#     res=get_tdd(U,[var[3],var[1],var[2],var[0]],idx_2_key) 
#     res.index_2_key=idx_2_key
#     res.key_2_index=key_2_idx
#     res.index_set=[var[0],var[1],var[2],var[3]]
#     res.key_width[0]=res.key_width[1]=res.key_width[2]=res.key_width[3]=2
#     return res