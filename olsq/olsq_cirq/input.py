from cirq import Circuit


def input_cirq(circuit: Circuit, map_physical_qubit_to: dict):
    """Handle a Cirq circuit object as input.
    In Cirq, the qubits are objects, in OLSQ IR, qubits are integers, so
    we need to store a mapping from indices to Cirq qubits.

    Args:
        circuit: a Cirq Circuit object
        map_physical_qubit_to: a mapping from Cirq qubits to indices

    Returns:
        count_program_qubit: in OLSQ IR
        list_gate_qubits: in OLSQ IR
        list_gate_name: in OLSQ IR, not merely string, but Cirq objects
    """

    list_gate_qubits = []
    list_gate_name = []

    for operation in circuit.all_operations():
        list_gate_name.append(operation.gate)
        if len(operation.qubits) == 1:
            list_gate_qubits.append(
                (map_physical_qubit_to[operation.qubits[0]],) )
        elif len(operation.qubits) == 2:
            list_gate_qubits.append(
                (map_physical_qubit_to[operation.qubits[0]],
                 map_physical_qubit_to[operation.qubits[1]]  )  )
        else:
            raise ValueError("Only support single-qubit and two-qubit gates.")

    return [len(circuit.all_qubits()), tuple(list_gate_qubits),
            tuple(list_gate_name)]
