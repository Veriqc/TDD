# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 17:01:47 2020

@author: zxz58
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 18:57:54 2019

@author: Xiangzhen Zhou

"""

from qiskit.circuit import Gate
# from qiskit.extensions import standard
# from qiskit.providers.aer.extensions import standard
# from qiskit.extensions.standard.cx import CnotGate
class OperationU(object):
    '''
    Unitary operation
    '''
    
    instances_count = 0
    
    def __init__(self, qbits, name, u_matrix=None, d_o=[]):
        '''
        qbits: list of all input qubits
        name: name of operation, i.e., CX...
        d_qs: list of dependent operations
        '''
        self.involve_qubits = qbits
        self.input_qubits = self.involve_qubits
        self.involve_qubits_list = []
        self.name = name
        self.u_matrix = u_matrix
        for q in qbits:
            #print(isinstance(q, QR))
            #print(type(q))
            if isinstance(q, int): q = [int(q), int(q)]
            self.involve_qubits_list.append(int(q[1]))
        self.dependent_operations = list(set(d_o))
        self.DeleteRedundantDependentOperation()
        self._RefreshDependencySet()
        OperationU.instances_count = OperationU.instances_count + 1
        
    def _RefreshDependencySet(self):
        self.dependency_set = []
        if self.dependent_operations != []:
            for dependent_operation in self.dependent_operations:
                self.dependency_set.extend(dependent_operation.dependency_set)
                self.dependency_set.append(dependent_operation)
        # remove reduplicative elements
        self.dependency_set = list(set(self.dependency_set))
    
    def DeleteRedundantDependentOperation(self):
        '''
        delete some dependent operations that already have dependent relationship
        '''
        if self.dependent_operations != []:
            for current_operation in self.dependent_operations:
                flag = False
                for test_operation in self.dependent_operations:
                    if current_operation in test_operation.dependency_set:
                        flag = True
                        break
                if flag == True:
                    self.dependent_operations.remove(current_operation)
    
    def InvolveQubitsList(self):
        return self.involve_qubits_list.copy()

class OperationCNOT(OperationU):
    '''
    CNOT Unitary operation
    '''
    
    instances_count = 0
    
    def __init__(self, c_q, t_q, d_o=[]):
        '''
        d_qs: list of dependent operations
        '''
        self.control_qubit = c_q
        self.target_qubit = t_q
        super().__init__([c_q, t_q], 'CX', None, d_o)
        OperationCNOT.instances_count = OperationCNOT.instances_count + 1
        

class OperationSingle(OperationU):
    '''arbitrary single qubit operation, U3 in qiskit'''
    def __init__(self, q_in, u_matrix=None, name='single', d_o=[]):
        '''
        d_qs: list of dependent operations
        '''
        super().__init__([q_in], name, u_matrix, d_o)

class OperationTwo(OperationU):
    '''arbitrary two-qubit operation in qiskit'''
    def __init__(self, q_list, u_matrix=None, name='two', d_o=[]):
        '''
        d_qs: list of dependent operations
        '''
        super().__init__(q_list, name, u_matrix, d_o)