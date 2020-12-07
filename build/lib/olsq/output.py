from olsq.device import qcdevice


def output_qasm(device: qcdevice, result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits, final_mapping,
                if_measure: bool, file_name=None):
    count_physical_qubit = device.count_physical_qubit
    swap_duration = device.swap_duration
    list_moment = ["" for i in range(result_depth)]

    for t in range(result_depth):
        for j, qubits in enumerate(list_scheduled_gate_qubits[t]):
            if isinstance(qubits, int):
                list_moment[t] += "{} q[{}];\n".format(list_scheduled_gate_name[t][j], qubits)
            else:
                list_moment[t] += "{} q[{}], q[{}];\n".format(list_scheduled_gate_name[t][j], qubits[0], qubits[1])

    output_str = str()
    output_str += "".join(
        ['\n', "OPENQASM 2.0;\n", "include \"qelib1.inc\";\n", "qreg q[{}];\n".format(count_physical_qubit),
         "creg c[{}];\n".format(count_physical_qubit)])
    for t in range(result_depth):
        output_str += "".join(['\n', "// cycle {}\n".format(t)])
        output_str += list_moment[t]
    if if_measure:
        output_str += "\n// measurement\n"
        for program_qubit, physical_qubit in enumerate(final_mapping):
            output_str += "measure q[{}] -> c[{}];\n".format(physical_qubit, program_qubit)

    if file_name:
        output_file = open(file_name, "w")
        output_file.write(output_str)

    return output_str
