import numpy as np
import itertools

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

def perms_generator(n):
    """Yield n-bit binary rep string from 00...00 to 11...11"""
    for i in range(2**n):
        s = bin(i)[2:]
        s = "0"*(n-len(s)) + s
        yield s

def matrix_2_tensor(U, n):
    """Transform qiskit n-qubit gate matrix U_{yx} to tensor T_{xx'yy'}"""
    assert U.shape[0] == U.shape[1]
    T = np.zeros( (2,)*(2*n), dtype=U.dtype )
    
    # bit_strs = list(perms_generator(n))
    # we have to reverse the bit order x[::-1]
    bit_tuples = [tuple(map(lambda d: int(d), x[::-1])) for x in perms_generator(n)]
    for u_index, tensor_index_in in enumerate(bit_tuples):
        for u_index2, tensor_index_out in enumerate(bit_tuples):
            tensor_index = tuple(itertools.chain(*zip(tensor_index_in, tensor_index_out)))
            T[tensor_index] = U[u_index2][u_index]
            print(f'T[{tensor_index}]', f'U[{u_index2}][{u_index}]={U[u_index2][u_index]}')
    return T