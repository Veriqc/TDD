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
A tensor in TDD can be defined as follows:

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

    var2=[Index('y0'),Index('x1')]
    ts2=Tensor(U,var2)
    tn=TensorNetwork([ts1,ts2])
    
You can use floowing instructions to obtain the TDD of the tensor network and the corresponding graph.

    tdd=tn.cont()
    tdd.show()

### Quantum Circuits
TDD_Q


