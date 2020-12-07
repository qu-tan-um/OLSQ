from cirq import Circuit


def input_cirq(circuit: Circuit):
    map_program_qubit_to = []
    map_to_program_qubit = dict()
    count_program_qubit = len(circuit.all_qubits())
    for i, qubit in enumerate(circuit.all_qubits()):
        map_program_qubit_to.append(qubit)
        map_to_program_qubit[qubit] = i

    list_gate_qubits = []
    list_gate_name = []

    for operation in circuit.all_operations():
        list_gate_name.append(operation.gate)
        if len(operation.qubits) == 1:
            list_gate_qubits.append(map_to_program_qubit[operation.qubits[0]])
        elif len(operation.qubits) == 2:
            list_gate_qubits.append((map_to_program_qubit[operation.qubits[0]],
                                     map_to_program_qubit[operation.qubits[1]]))
        else:
            raise Exception("Only support single- and two-qubit gates")

    return [count_program_qubit, list_gate_qubits, list_gate_name, map_program_qubit_to]
