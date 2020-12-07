def input_qasm(circ_str):
    qasm = circ_str.splitlines()
    gates = list()
    gate_spec = list()
    qubit_num = 0
    for line in qasm:
        # print(line)
        line = line.split()
        grammar = len(line)
        if line:
            if line[0] == 'OPENQASM':
                continue
            if line[0] == 'include':
                continue
            if line[0] == 'creg':
                continue
            if line[0] == 'measure':
                continue
            if line[0] == 'qreg':
                qubit_num = int(line[1][2:-2])
                continue
            if line[0] == '//':
                continue
            if line[0] == 'cx' or line[0] == 'zz':
                if grammar == 3:
                    qubit0 = int(line[1][2:-2])
                    qubit1 = int(line[2][2:-2])
                elif grammar == 2:
                    qubits = line[1].split(',')
                    qubit0 = int(qubits[0][2:-1])
                    qubit1 = int(qubits[1][2:-2])
                gates.append((qubit0, qubit1))
                gate_spec.append(line[0])
            elif grammar == 2:
                qubit = int(line[1][2:-2])
                gates.append(qubit)
                gate_spec.append(line[0])

    return [qubit_num, gates, gate_spec]


