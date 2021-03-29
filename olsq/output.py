from olsq.device import qcdevice


def output_qasm(device: qcdevice, result_depth: int,
                list_scheduled_gate_name: list,
                list_scheduled_gate_qubits: list,
                final_mapping: list, if_measure: bool, file_name: str = None):
    """Generate qasm output
    By default: 1) the qasm sentences are separated by newline,
    2) there is a comment before every moment in the circuit, and
    3) from the measurement, we can read of the final mapping. 
    If in the original circuit (input to OLSQ) a qubit has index i,
    then it will be measured at c[i] in the qasm string.

    Args:
        device: use the same QC device as in OLSQ.setdevice()
        result_depth: depth of the scheduled circuit
        list_scheduled_gate_name: type/name of each gate
        list_scheduled_gate_qubits: which qubit(s) each gate acts on
        final_mapping: mapping from logical qubits to physical qubits
        if_measure: if measure all qubits in the end
        file_name: (optional) a file to put the qasm string

    Returns:
        output_str: a qasm string in the above mentioned format.
    """

    count_physical_qubit = device.count_physical_qubit
    swap_duration = device.swap_duration
    
    # a list of strings, each string represents a moment in the circuit
    list_moment = ["" for i in range(result_depth)]
    for t in range(result_depth):
        for j, qubits in enumerate(list_scheduled_gate_qubits[t]):
            if len(qubits) == 1:
                list_moment[t] += list_scheduled_gate_name[t][j]
                list_moment[t] += f" q[{qubits[0]}];\n"
            else:
                list_moment[t] += list_scheduled_gate_name[t][j]
                list_moment[t] += f" q[{qubits[0]}], q[{qubits[1]}];\n"

    output_str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    output_str += f"qreg q[{count_physical_qubit}];\n"
    output_str += f"creg c[{count_physical_qubit}];\n"
    for t in range(result_depth):
        output_str += f"\n// moment {t}\n"
        output_str += list_moment[t]
    
    if if_measure:
        output_str += "\n// measurement\n"
        for program_qubit, physical_qubit in enumerate(final_mapping):
            output_str += f"measure q[{physical_qubit}]->c[{program_qubit}];\n"

    if file_name is not None:
        output_file = open(file_name, "w")
        output_file.write(output_str)

    return output_str
