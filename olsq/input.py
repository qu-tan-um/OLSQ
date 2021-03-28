def input_qasm(circ_str: str):
    """ process an input qasm string
    This is a simple qasm parser that works on many qasm files that I know of.
    The current OLSQ formulation only support single-qubit gates and two-qubit
    gates, so only those are processed.  This parser has some more assumptions:
    1) each instruction starts in a new line, 2) two-qubit gates are cx or zz,
    and 3) there is only one array of qubits.

    Args:
        circ_str: a string in qasm format.

    Returns:
        a list [qubit_num, gates, gate_spec]
            qubit_num: logical qubit number.
            gates: which qubit(s) each gate acts on.
            gate_spec: type of each gate.

    Example:
        for the following circuit 
            q_0: ───────────────────■───
                                    │  
            q_1: ───────■───────────┼───
                 ┌───┐┌─┴─┐┌─────┐┌─┴─┐
            q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
                 └───┘└───┘└─────┘└───┘ 
        gates = ((2,), (1,2), (2,), (0,1))
        gate_spec = ("h", "cx", "tdg", "cx")
    """

    gates = list() # which qubit(s) each gate acts on
    gate_spec = list() # type of each gate
    qubit_num = 0

    for qasmline in circ_str.splitlines():
        words = qasmline.split()
        if not isinstance(words, list): continue # empty lines
        
        grammar = len(words)
        # grammer=2 -> single-qubit gate type then one qubit
        #              |two-qubit gate type then two qubits separated by ","
        # grammer=3 -> two-qubit gate type then two qubits separated by ", "
        # grammer=1 or >3 -> incorrect, raise an error
        
        if words[0] in ["OPENQASM", "include", "creg", "measure", "//"]:
            continue

        if words[0] == 'qreg':
            qubit_num = int(words[1][2:-2])
            continue
        
        if words[0] == 'cx' or words[0] == 'zz':
            if grammar == 3: # qubits are separated by a comma and a space
                try:
                    qubit0 = int(words[1][2:-2])
                    qubit1 = int(words[2][2:-2])
                except:
                    raise ValueError(f"{qasmline} invalid two-qubit gate.")
            
            elif grammar == 2: # qubits are not separated by only a comma
                qubits = words[1].split(',')
                try:
                    qubit0 = int(qubits[0][2:-1])
                    qubit1 = int(qubits[1][2:-2])
                except:
                    raise ValueError(f"{qasmline} invalid two-qubit gate.")
            
            else:
                raise ValueError(f"{qasmline}: invalid two-qubit gate.")
            
            gates.append((qubit0, qubit1))
            gate_spec.append(words[0])
        
        elif grammar == 2: # not two-qubit gate, and has two words
            try:
                qubit = int(words[1][2:-2])
            except:
                raise ValueError(f"{qasmline} invalid single-qubit gate.")
            gates.append((qubit,))
            gate_spec.append(words[0])
        
        else:
            raise ValueError(f"{qasmline} invalid gate.")

    if qubit_num == 0:
        raise ValueError("Qubit number is not specified.")
    return [qubit_num, tuple(gates), tuple(gate_spec)]
