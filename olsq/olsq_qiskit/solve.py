from olsq.solve import OLSQ
from qiskit import QuantumCircuit
from olsq.device import qcdevice
from olsq.input import input_qasm


class OLSQ_qiskit(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        super().__init__(objective_name, if_transition_based)

    def setdevicegraph(self, device, mode=None):
        if mode == "ibm":
            config = device.configuration()
            edges = config.coupling_map
            biedges = []

            for edge in edges:
                qubit0 = edge[0]
                qubit1 = edge[1]
                if qubit0 > qubit1:
                    tmp = qubit0
                    qubit0 = qubit1
                    qubit1 = tmp
                
                if [qubit0, qubit1] not in biedges:
                    biedges.append([qubit0, qubit1])
            print(biedges)
            super().setdevice(qcdevice(config.backend_name, nqubits=config.n_qubits, connection=biedges, swap_duration=3))
        else:
            super().setdevice(device)

    def setprogram(self, circuit_qiskit=None, input_mode=None):
        if circuit_qiskit is None:
            raise Exception("no input program")

        if input_mode == "qasm":
            program_qiskit= input_qasm(circuit_qiskit)
        else:
            circuit_qiskit = circuit_qiskit.decompose()
            program_qiskit= input_qasm(circuit_qiskit.qasm())
        
        super().setprogram([program_qiskit[0], program_qiskit[1], program_qiskit[2]], input_mode="IR")


    def solve(self, output_mode=None, output_file_name=None):
        circuit_str, final_mapping = super().solve()
        circuit = QuantumCircuit()
        circuit = circuit.from_qasm_str(circuit_str)
        return [circuit, final_mapping]