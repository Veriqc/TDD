# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 12:37:42 2020

@author: zxz58
"""
import networkx as nx
from cir_input.qasm import CreateCircuitFromQASM
from qiskit.quantum_info.operators import Operator
from cir_input.gate_operation import OperationCNOT, OperationSingle, OperationTwo
import numpy as np

def CreateDGfromQASMfile(QASM_file, path,
                         flag_single=True,
                         flag_interaction=False):
    '''
    convert QASM file to cir and DG
    
    DG is a directed graph where each node represents a quantum gate and egde
    dependency
        if you want to get the u_matrix of a node i,
        use DG.nodes[i]['operation'].u_matrix
        
        if you want to get a list of node i in whcih each element represents
        the qubit index where the gate in node i operates,
        use DG.nodes[i]['operation'].involve_qubits_list
        
        if you want to get the qiskit gate data of a node i,
        use DG.nodes[i]['operation'].qiskit_data
    
    flag_single: whether we should convert single qubit gate
    
    flag_interaction: whether we should generate interaction matrix in which
        each entry represents # CNOT between column and raw qubits. It can be
        invoked by 'DG.interaction_matrix'
    output:
        circuit, (DG, num_unidentified_gates)
    '''
    cir = CreateCircuitFromQASM(QASM_file, path)
    res = QiskitCircuitToDG(cir, flag_single, flag_interaction)
    return cir, res

def QiskitCircuitToDG(cir,
                      flag_single=False,
                      flag_interaction=False):
    '''
    convert Qiskit circuit to DG
    support only CNOT and single qubit gates
    flag_single: whether we should convert single qubit gate
    '''
    operations = []
    num_unidentified_gates = 0
    qregs = cir.qregs
    if len(qregs) > 1:
        raise Exception('quantum circuit has more than 1 quantum register')
    q = qregs[0]
    interaction_matrix = np.zeros((len(q), len(q))) if flag_interaction == True else None
    data = cir.data
    for gate in data:
        if flag_interaction == True:
            if len(gate[1]) == 2:
                interaction_matrix[gate[1][0].index][gate[1][1].index] += 1
                interaction_matrix[gate[1][1].index][gate[1][0].index] += 1
        operation = QiskitGateToOperation(gate, flag_single)
        operation.qiskit_data = gate
        if operation == None:
            num_unidentified_gates += 1
        else:
            operations.append(operation)
    GenerateDependency(operations, q.size)
    DG = OperationToDependencyGraph(operations)
    DG.interaction_matrix = interaction_matrix
    return DG, num_unidentified_gates

def QiskitGateToOperation(Gate, flag_single=False):
    '''
    ATTENTION: The input gate should only be cx or single-qubit gates
    convert a Qiskit Gate object to OperationU
    only support CNOT and single qubit gates
    flag_single: whether we should convert single qubit gate
    '''

    '''old qiskit version'''
# =============================================================================
#     if Gate.name == 'cx':
#         qargs = Gate.qargs
#         return OperationCNOT(qargs[0], qargs[1])
# =============================================================================
    '''new qiskit version'''
    if Gate[0].name == 'cx':
        qargs = Gate[1]
        return OperationCNOT(qargs[0].index, qargs[1].index)
    else:
        if flag_single == True:
            '''convert single-qbuit gate'''
            qiskit_gate = Gate[0]
            u_matrix = Operator(qiskit_gate).data
            qargs = Gate[1]
            if len(qargs) == 1:
                return OperationSingle(qargs[0].index, u_matrix=u_matrix,name=Gate[0].name)  
            if len(qargs) == 2:
                return OperationTwo([qargs[0].index, qargs[1].index], u_matrix=u_matrix)
    return None

def GenerateDependency(operations, num_q):
    '''Generate Dependency to operations according to the order'''
    dic = {}
    for i in range(num_q):
        dic[i] = None
    
    for operation in operations:
        qubits = operation.involve_qubits
        for q in qubits:
            if isinstance(q, int): q = [int(q), int(q)]
            if dic[q[1]] == None:
                dic[q[1]] = operation
            else:
                dependent_operation = dic[q[1]]
                if not dependent_operation in operation.dependent_operations:
                    operation.dependent_operations.append(dependent_operation)
                dic[q[1]] = operation

def OperationToDependencyGraph(operations):
    '''
    create dependency graph
    input:
        operations a list of all operations instances
    '''
    first_gates = [-1]*100 #a list in which each element is the node that takes the first place of qubits
    last_gates = [-1]*100
    
    num_vertex = len(operations)
    DG = nx.DiGraph()
    num_q_log = 0
    DG.add_nodes_from(list(range(num_vertex)))
    for i in range(num_vertex):
        current_operation = operations[i]
        qubits = current_operation.InvolveQubitsList()
        for qubit in qubits:
            if first_gates[qubit] == -1: first_gates[qubit] = i
            last_gates[qubit] = i
            if qubit + 1 > num_q_log: num_q_log = qubit + 1
        DG.add_node(i, operation = current_operation)
        if current_operation.dependent_operations != []:
            DG.add_node(i, root = False)
            for current_de in current_operation.dependent_operations:
                DG.add_edge(operations.index(current_de), i)
        else:
            DG.add_node(i, root = True)
    DG.first_gates = first_gates
    DG.last_gates = last_gates
    DG.num_q_log = num_q_log
    return DG

def FindExecutableNode(dependency_graph,
                       executed_vertex=None,
                       executable_vertex=None,
                       removed_vertexes=None):
    '''
    WHEN executable_vertex = None:
        Use dependency graph to find the executable vertexes/nodes, i.e., nodes
        in current level
        return:
            executable_nodes: a list of nodes. If no executable node, return []
    WHEN both executed_vertex and executable_vertex != None:
        only update executed_vertex and executable_vertex according to newly
        executed gates (removed_vertexes)
        return:
            executable_vertex      
    '''
    DG = dependency_graph
    if executable_vertex == None:
        degree = DG.in_degree
        executable_nodes = []
        for i in degree:
            if i[1] == 0:
                executable_nodes.append(i[0])
    else:
        executable_nodes = executable_vertex
        for removed_vertex in removed_vertexes:
            if not removed_vertex in executable_vertex: raise Exception('removed node is not executable')
            candidate_nodes = DG.successors(removed_vertex)
            executable_nodes.remove(removed_vertex)
            executed_vertex.append(removed_vertex)
            #DG.remove_node(removed_vertex)
            for node in candidate_nodes:
                flag_add = True
                '''check whether this node is executable'''
                for pre_node in DG.predecessors(node):
                    if not pre_node in executed_vertex:
                        flag_add = False
                        break
                if flag_add == True: executable_nodes.append(node)
    return executable_nodes

def AddLevelNumToDG(DG):
    '''
    Add level number to DG, this number can be obtained via
    DG.nodes[node][lev_num]
    '''
    executable_vertex = FindExecutableNode(DG)
    removed_vertexes = []
    executed_vertex = []
    lev_num = 0
    while len(executable_vertex) !=0:
        for node in executable_vertex:
            DG.nodes[node]['lev_num'] = lev_num
        removed_vertexes = executable_vertex.copy()
        executable_vertex = FindExecutableNode(DG,
                                               executed_vertex,
                                               executable_vertex,
                                               removed_vertexes)
        lev_num += 1
    

if __name__ == '__main__':
    QASM_file = 'test3.qasm'
    path = 'C:/ProgramData/Anaconda3/Lib/site-packages/circuittransform/inputs/QASM example/'
    cir, res = CreateDGfromQASMfile(QASM_file, path, flag_single=True)
    DG, _ = res
    AddLevelNumToDG(DG)
    nx.draw(DG, with_labels=True)
    from cir_split import SplitDG
    res = SplitDG(DG,
                  max_cut_cx=1,
                  ini_part_A_qubits=[0, 1],
                  ini_part_B_qubits=[2, 3, 4])
    print(res)