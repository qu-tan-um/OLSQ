from qiskit import QuantumCircuit


def qiskit_info_original(file_name, new_file_name):
    original_circ = QuantumCircuit.from_qasm_file(file_name)
    original_depth = original_circ.depth()
    original_gate_count = original_circ.count_ops()
    print("depth =", original_depth)
    print("gate count =", original_gate_count)
    with open(new_file_name + ".txt", 'w') as file:
        file.write("before:\n")
        file.write("depth " + str(original_depth) + '\n')
        for type, count in original_gate_count.items():
            file.write(type + ' ' + str(count) + '\n')
    file.close()
    original_cx_count = original_gate_count['cx']
    return [original_depth, original_cx_count]

def qiskit_info_after(circ, new_file_name, original_cx_count):
    if isinstance(circ, str):
        circ = QuantumCircuit.from_qasm_file(circ)
    circ_qiskit = circ.decompose()

    circ_qiskit.qasm(filename=new_file_name + '.qasm')
    print(circ_qiskit)
    depth = circ_qiskit.depth()
    gate_count = circ_qiskit.count_ops()
    print("depth =", depth)
    print("gate count =", gate_count)
    with open(new_file_name + ".txt", 'a') as file:
        file.write("after:\n")
        file.write("depth " + str(depth) + '\n')
        for type, count in gate_count.items():
            file.write(type + ' ' + str(count) + '\n')
        additional_cx_count = gate_count['cx'] - original_cx_count
        file.write("additional cx " + str(additional_cx_count))
    file.close()
    return additional_cx_count
