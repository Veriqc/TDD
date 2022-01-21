# A-Tensor-Network-Based-Decision-Diagram
## Overview
Decision diagrams have been used in simulation and equivalence checking of quantum circuits. Inspired by the efficienvy and flexibility of Tensor Networks. A tensor network-based decision diagram has been proposed in https://arxiv.org/abs/2009.02618. This repository gives a proof-of-concept implementation of the Tensor Decision Diagram(TDD) using Python3. 
Part of the benchmarks are coming from https://github.com/iic-jku/qmap/tree/master/examples.

## Dependencies
In order to use this package, you are expected to first install the fllowing packages: numpy, networkx, qiskit and graphviz. The data type of numpy is used to defined the data of a tensor in our package. Networkx will be used as part of a optimizer in this package. Qiskit is used for coping with Quantum Circuits and Graphviz is used for showing the graph of a TDD.

## Usage
There are three components of our package: TDD, TN, TDD_Q. TDD include the basic structure and operations of the tensor decision diagram. TN contains the basic definitions and operations of Tensor and Tensor Network. TDD_Q is used for coping with Quantum Circuits.

    from TDD.TDD import Ini_TDD
    from TDD.TN import Index,Tensor,TensorNetwork
    from TDD.TDD_Q import cir_2_tn,get_real_qubit_num,add_trace_line,add_inputs,add_outputs
  
### Tensor
A tensor in TDD can be defined as follows. Note that there is no need for these tensors to be the shape of (2,2,...), it can be any shape, i.e. (n1,n2,...).

    U = np.array([[1,1],[1,-1]])
    var = [Index('x0'),Index('y0')]
    ts1 = Tensor(U,var)
    
Before using TDD, you need first assign a index order for all the indices:

    Ini_TDD(['x0','y0','x1','y1'])
    
Then, you can used following instructions to obtain the TDD and the corresponding graph of the TDD.
    
    tdd1 = ts1.tdd()
    tdd1.show()
    
### Tensor Networks
A tensor network is defined by a set of tensors:
    
    V = np.array([[1,0],[0,1]])
    var2 = [Index('y0'),Index('x1')]
    ts2 = Tensor(V,var2)
    tn = TensorNetwork([ts1,ts2])
    
You can use floowing instructions to obtain the TDD of the tensor network and the corresponding graph.

    tdd = tn.cont()
    tdd.show()

### Quantum Circuits
TDD_Q provide the function for transforming a Qiskit QuantumCircuit as a Tensor Network.

    path = 'Benchmarks/'
    file_name = "3_17_13.qasm"
    cir = QuantumCircuit.from_qasm_file(path+file_name)
    tn, all_indexs = cir_2_tn(cir) # all_indexs gives all the indices used in this t=TensorNetwork
    
You can also add inputs and outputs to this circuit. At present, only computation basis are allowed. Or you can also add the trace line to calculate the trace of the corresponding circuit.

    n = get_real_qubit_num(cir)
    input_s = [0]*n
    output_s = [0]*n
    if input_s:
        add_inputs(tn,input_s,n)
    #if output_s:
    #    add_outputs(tn,output_s,n)
    # add_trace_line(tn,n)
    
Then fllowing instructions can be used to obatain the corresponding TDD.

    Ini_TDD(index_order=all_indexs) # the index_order can be arbitrary assigned.
    tdd=tn.cont()
    tdd.show()

If the final TDD represent a quantum state, you can use the following instructions to obtain a measurement result or do sampling or obtain an amplitude.
    
    print(tdd.measure())
    print(tdd.sampling(10))
    print(tdd.get_amplitude([0]*n))
    
### Optimizers
There are currently three optimizers can be used for contracting a Tensor Network.

    tdd = tn.cont(optimizer='tree_decomposition')
Or, 

    tdd = tn.cont(optimizer='cir_partition1')
Or, 

    tdd = tn.cont(optimizer='cir_partition2')
   
If you do not assign the optimizer, the TensorNetwork can be contracted as the order of tensors appeared in tn. The optimizer 'tree_decomposition' is build upon networkx, and the optimizer 'cir_partition1' and 'cir_partition2' can only be used when this Tensor Network represent a Quantum Circuit.

### Equivalence Checking
To check the equivalence of two quantum circuits or two tensors, you just need to construct the TDDs of these two quantum circuits or tensors using the same index order and then check the equivalence of the two TDDs. Note that, the indices and the index order of the final tensors must be matched. Otherwise, it will do not gives the right answer.

    file_name2 = "3_17_13_2.qasm"
    cir2 = QuantumCircuit.from_qasm_file(path+file_name2)
    tn2, all_indexs2 = cir_2_tn(cir2)
    set_index_order(all_indexs2) 
    tdd2=tn2.cont() # Notice that the final indices of tdd2 must match that of tdd
    print(tdd==tdd2)
    
