from olsq.solve import OLSQ
from olsq.olsq_cirq.input import input_cirq
from cirq import Circuit, Moment, GateOperation, SWAP
from olsq.device import qcdevice


class OLSQ_cirq(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        super().__init__(objective_name, if_transition_based)
        self.map_program_qubit_to = []
        self.map_to_cirq_qubit = []

    def setdevicegraph(self, device_graph):
        map_cirq_qubit_to = dict()
        count_physical_qubit = len(list(device_graph.nodes()))
        for i, qubit in enumerate(list(device_graph.nodes())):
            self.map_to_cirq_qubit.append(qubit)
            map_cirq_qubit_to[qubit] = i

        qubit_edges = []
        for edge in list(device_graph.edges()):
            qubit_edges.append([map_cirq_qubit_to[edge[0]], map_cirq_qubit_to[edge[1]]])

        super().setdevice(qcdevice("tmp", count_physical_qubit, qubit_edges, 1))

    def setprogram(self, program_cirq=None, input_mode=None):
        if program_cirq is None:
            raise Exception("no input program")

        if input_mode is None:
            program_cirq = input_cirq(program_cirq)
        super().setprogram([program_cirq[0], program_cirq[1], program_cirq[2]], input_mode="IR")

        self.map_program_qubit_to = program_cirq[3]

    def solve(self, output_mode=None, output_file_name=None):
        result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits, final_mapping = super().solve("IR")
        circuit = Circuit()
        for t in range(result_depth):
            moment = Moment()
            for i, qubits in enumerate(list_scheduled_gate_qubits[t]):
                if isinstance(qubits, int):
                    moment = moment.with_operation(GateOperation(list_scheduled_gate_name[t][i],
                                                                 (self.map_to_cirq_qubit[qubits], )))
                else:
                    if list_scheduled_gate_name[t][i] == "SWAP":
                        moment = moment.with_operation(GateOperation(SWAP,
                                                                     (self.map_to_cirq_qubit[qubits[0]],
                                                                      self.map_to_cirq_qubit[qubits[1]])))
                    else:
                        moment = moment.with_operation(GateOperation(list_scheduled_gate_name[t][i],
                                                                     (self.map_to_cirq_qubit[qubits[0]],
                                                                      self.map_to_cirq_qubit[qubits[1]])))
            circuit += moment

        final_cirq_mapping = dict()
        for i in range(self.count_program_qubit):
            final_cirq_mapping[self.map_to_cirq_qubit[final_mapping[i]]] = self.map_program_qubit_to[i]

        return [circuit, final_cirq_mapping]
