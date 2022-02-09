# Tensor Diagram
import networkx as nx
from qiskit import QuantumCircuit
from .utils import *

class TensorDiagram:
    def __init__(self):
        pass

    @staticmethod
    def from_circuit(circuit: QuantumCircuit):
        """return a TensorDiagram contstructed from the provided QuantumCircuit"""
        hyper_index=dict()
        qubits_index = dict()
        start_tensors= dict()
        end_tensors = dict()
        num_qubits = get_real_qubit_num(circuit)

        td = TensorDiagram()

        for i in range(num_qubits):
            td.qubits_index[i] = 0

        gates = circuit.data

        for i, gate in enumerate(gates):
            instruction, qubits, _ = gate
            gate_name = instruction.name
            gate_qubits = [q.index for q in qubits]
            # we not only consider CX gate but also other Ctrl-U gates
            U = instruction.to_matrix()
            if len(gate_qubits) > 1:
                T = matrix_2_tensor(U, len(gate_qubits))
            else:
                T = U
        # TODO
