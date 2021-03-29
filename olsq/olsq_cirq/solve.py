from cirq import Circuit, Moment, GateOperation, SWAP
import networkx as nx

from olsq.solve import OLSQ
from olsq.device import qcdevice
from olsq.olsq_cirq.input import input_cirq


class OLSQ_cirq(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        """Set the objective of OLSQ_cirq, and whether transition-based.

        Args:
            objective_name: can be "depth", "swap", or "fidelity"
            mode: can be "normal" or "transition" (TB-OLSQ in the paper)       
        """

        super().__init__(objective_name, if_transition_based)
        self.map_physical_qubit_to = dict() # Cirq qubit |-> qubit index
        self.map_to_physical_qubit = []     # qubit index |-> Cirq qubit

    def setdevicegraph(self, device_graph: nx.Graph):
        """Pass in a graph representing hardware in Cirq, also generate
        a mapping from indices to physical qubits, and reverse mapping.

        Args:
            device_graph: an NetworkX Graph object where vertices are
                Cirq qubits and edges mean physical connections.
                Some code in Cirq use this representation of QC devices.
        """

        count_physical_qubit = len(list(device_graph.nodes()))
        for i, qubit in enumerate(list(device_graph.nodes())):
            self.map_to_physical_qubit.append(qubit)
            self.map_physical_qubit_to[qubit] = i

        qubit_edges = []
        for edge in list(device_graph.edges()):
            qubit_edges.append( (map_physical_qubit_to[edge[0]],
                                 map_physical_qubit_to[edge[1]]) )

        super().setdevice(
            qcdevice("cirq-dev", nqubits=count_physical_qubit,
                     connection=tuple(qubit_edges), swap_duration=1) )

    def setprogram(self, program_cirq: Circuit):
        """Translate input Cirq program/circuit to IR

        Args:
            program_cirq: a Circuit object in Cirq
        """

        program_cirq = input_cirq(program_cirq, self.map_physical_qubit_to)
        super().setprogram(program_cirq, input_mode="IR")

    def solve(self):
        """Use the super().solve(...) and output result in Cirq

        Returns:
            circuit: result in Cirq Circuit object
            final__cirq_mapping: from input Cirq qubit to Cirq qubit
            objective_value: depth/#swap/fidelity depending on setting

        Note:
            final_mapping (returned by super().solve(...)): 
                logical qubit index |-> physical qubit index
            map_to_physical_qubit: qubit index |-> Cirq qubit
            So the final mapping should be m(i) |-> m(f(i))
        """

        result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits,\
            final_mapping, objective_value = super().solve(output_mode="IR")
        
        # constructing the output Cirq Circuit object
        circuit = Circuit()
        for t in range(result_depth):
            moment = Moment()
            for i, qubits in enumerate(list_scheduled_gate_qubits[t]):
                if len(qubits) == 1:
                    moment = moment.with_operation( 
                        GateOperation( list_scheduled_gate_name[t][i],
                            (self.map_to_physical_qubit[qubits],)      ) )
                else:
                    if list_scheduled_gate_name[t][i] == "SWAP":
                        moment = moment.with_operation(
                            GateOperation(SWAP, 
                                (self.map_to_physical_qubit[qubits[0]],
                                 self.map_to_physical_qubit[qubits[1]]) ) )
                    else:
                        moment = moment.with_operation(
                            GateOperation(list_scheduled_gate_name[t][i],
                                (self.map_to_physical_qubit[qubits[0]],
                                 self.map_to_physical_qubit[qubits[1]])   ) )
            circuit += moment

        final_cirq_mapping = dict()
        for i in range(self.count_program_qubit):
            final_cirq_mapping[ self.map_to_physical_qubit[i] ] = \ 
                self.map_to_physical_qubit[ final_mapping[i] ]

        return [circuit, final_cirq_mapping, objective_value]
