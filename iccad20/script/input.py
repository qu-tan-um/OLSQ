import sys
import os

def read_qasm(file_name):
    f = open(file_name, 'r')
    qasm = f.readlines()
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
            if (line[0] == 'cx' or line[0] == 'zz'):
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

    f.close()
    return [qubit_num, gates, gate_spec]


def dependency_extracting(g):
    # dependency set
    D = list()
    L = len(g)
    for l in range(L):
        for ll in range(l + 1, L):
            if isinstance(g[l], int) and isinstance(g[ll], int):
                if g[l] == g[ll]:
                    D.append((l, ll))
            if isinstance(g[l], int) and isinstance(g[ll], int) == False:
                if g[l] == g[ll][0] or g[l] == g[ll][1]:
                    D.append((l, ll))
            if isinstance(g[l], int) == False and isinstance(g[ll], int):
                if g[l][0] == g[ll] or g[l][1] == g[ll]:
                    D.append((l, ll))
            if isinstance(g[l], int) == False and isinstance(g[ll], int) == False:
                if (g[l][0] == g[ll][0] or g[l][0] == g[ll][1]) or (g[l][1] == g[ll][0] or g[l][1] == g[ll][1]):
                    D.append((l, ll))
    D_len = len(D)

    """
    DAG_depth = [1 for l in range(L)]
    max_input_depth = 1
    for dep in D:
        if DAG_depth[dep[1]] < DAG_depth[dep[0]] + 1:
            DAG_depth[dep[1]] = DAG_depth[dep[0]] + 1
        if DAG_depth[dep[1]] > max_input_depth:
            max_input_depth = DAG_depth[dep[1]]
    print("Longest dependency chain has {} gates.".format(max_input_depth))
    """

    return D
