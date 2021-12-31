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
