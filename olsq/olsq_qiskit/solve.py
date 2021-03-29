from qiskit import QuantumCircuit

from olsq.solve import OLSQ
from olsq.device import qcdevice
from olsq.input import input_qasm


class OLSQ_qiskit(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        """Set the objective of OLSQ_cirq, and whether transition-based.
        """

        super().__init__(objective_name, if_transition_based)

    def setdevice(self, device, mode: str = None):
        """Pass in a device representing hardware in Qiskit.

        Args:
            device: can be a qcdevice in OLSQ, or an IBM backend
            mode: if set to "ibm", process device as an IBM backend.
        """

        if mode == "ibm":
            config = device.configuration()
            edges = config.coupling_map # each edge has two tuples in this
            biedges = [] # represent each edge with one tuple

            for edge in edges:
                qubit0 = edge[0]
                qubit1 = edge[1]
                if qubit0 > qubit1:
                    tmp = qubit0
                    qubit0 = qubit1
                    qubit1 = tmp
                if (qubit0, qubit1) not in biedges:
                    biedges.append((qubit0, qubit1))

            super().setdevice(
                qcdevice(config.backend_name, nqubits=config.n_qubits,
                         connection=tuple(biedges), swap_duration=3    )  )
        else:
            super().setdevice(device)

    def setprogram(self, circuit: QuantumCircuit, input_mode: str = None):
        """Translate input Qiskit program/circuit to IR

        Args:
            circuit: a qasm string or a QuantumCircuit object in Qiskit
            input_mode: if set to "qasm", process curcyut as qasm
        """

        if input_mode == "qasm":
            program_qiskit = circuit
        else:
            circuit = circuit.decompose()
            program_qiskit = circuit.qasm()
        super().setprogram(program_qiskit)


    def solve(self):
        """Use the super().solve(...) and output in Qiskit

        Returns:
            circuit: result in Qiskit QuantumCircuit object
            final_mapping: from logical qubit to physical qubit
            objective_value: depth/#swap/fidelity depending on setting
        """

        circuit_str, final_mapping, objective_value = super().solve()
        circuit = QuantumCircuit()
        circuit = circuit.from_qasm_str(circuit_str)
        return [circuit, final_mapping, objective_value]