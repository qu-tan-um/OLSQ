from z3 import Int, IntVector, Bool, Optimize, Implies, And, Or, If, sat, set_param

from device import qcdevice
from input import read_qasm, dependency_extracting
import os
import time as sys_time
import sys
from ast import literal_eval
import math
from info import qiskit_info_after, qiskit_info_original


start_time = sys_time.time()

set_param("parallel.enable", True)
set_param("parallel.threads.max", 64)

file_name = sys.argv[1]
device_name = sys.argv[2]
objective_name = sys.argv[3]
# T = literal_eval(sys.argv[3])

device_test = qcdevice(device_name)
N = device_test.count_physical_qubit
e = device_test.connection_list
S = 1

[M, g, gate_spec] = read_qasm(file_name)
new_file_name = "result/paper/" + file_name.split('/')[-1].replace('.qasm', "_{}_tbolsq_{}".format(device_name, objective_name))


# pre-processing
K = len(e)
L = len(g)
print("Input gate count = {}".format(L))
if objective_name == "fidelity":
    f_1qbg = [int(1000 * math.log(device_test.fidelity_single_qubit[n])) for n in range(N)]
    #print(f_1qbg)
    f_2qbg = [int(1000 * math.log(device_test.fidelity_two_qubit[k])) for k in range(K)]
    #print(f_2qbg)
    f_meas = [int(1000 * math.log(device_test.fidelity_measurement[n])) for n in range(N)]
    #print(f_meas)
G_2 = list()
G_1 = list()
for l in range(L):
    if isinstance(g[l], int):
        G_1.append(l)
    else:
        G_2.append(l)
L_1 = len(G_1)
L_2 = len(G_2)

# adjacency set
A = list()
edge_list = list() # edges with this node
for n in range(N):
    A.append(list())
    edge_list.append(list())
for k in range(K):
    A[e[k][0]].append(e[k][1])
    A[e[k][1]].append(e[k][0])
    edge_list[e[k][0]].append(k)
    edge_list[e[k][1]].append(k)


# overlapping set
adj_edge = [[0] * K for k in range(K)]
O = list()
O_Len = list()
for k in range(K):
    O.append(list())
for k in range(K):
    for kk in range(k + 1, K):
        if (e[k][0] == e[kk][0] or e[k][0] == e[kk][1]) or (e[k][1] == e[kk][0] or e[k][1] == e[kk][1]):
            O[k].append(kk)
            O[kk].append(k)
            adj_edge[kk][k] = 1
            adj_edge[k][kk] = 1
for k in range(K):
    O_Len.append(len(O[k]))

D = dependency_extracting(g)
[T, original_cx_count] = qiskit_info_original(file_name, new_file_name)

# index function
I = [[0] * N] * N
for k in range(K):
    I[e[k][0]][e[k][1]] = k
    I[e[k][1]][e[k][0]] = k

T = 1
not_solve = True
while(not_solve):
    print("Trying maximal layers = {}...".format(T))

# Variables
# at cycle t, logical qubit q is mapped to pi[q][t]
    pi = [[Int("map_q{}_t{}".format(i, j)) for j in range(T)] for i in range(M)]

# time coordinate for gate l is time[l]
    time = IntVector('time', L)

# space coordinate for gate l is space[l]
    space = IntVector('space', L)

# if at cycle t, there is a SWAP finishing on edge k, then sigma[k][t]=1
    sigma = [[Bool("ifswap_e{}_t{}".format(i, j)) for j in range(T)] for i in range(K)]



# for swap optimization
    # if objective_name == "swap":
    num_swap = Int('num_swap')
# for fidelity optimization

    if objective_name == "fidelity":
        u = [Int("num_1qbg_p{}".format(n)) for n in range(N)]
        v = [Int("num_2qbg_e{}".format(k)) for k in range(K)]
        vv = [Int("num_swap_e{}".format(k)) for k in range(K)]
        w = [Int("num_meas_p{}".format(n)) for n in range(N)]
        fidelity = Int('log_fidelity')

    # else:
# for depth optimization
    depth = Int('depth')


    z3 = Optimize()


    """
    Constraints
    """

    for t in range(T):
        for m in range(M):
            z3.add(pi[m][t] >= 0, pi[m][t] < N)
            for mm in range(m):
                z3.add(pi[m][t] != pi[mm][t])

    for l in range(L):
        z3.add(time[l] >= 0, time[l] < T)
        if l in G_1:
            z3.add(space[l] >= 0, space[l] < N)
            for t in range(T):
                z3.add(Implies(time[l] == t, pi[g[l]][t] == space[l]))
        elif l in G_2:
            z3.add(space[l] >= 0, space[l] < K)
            for k in range(K):
                for t in range(T):
                    z3.add(Implies(And(time[l] == t, space[l] == k), Or(And(e[k][0] == pi[g[l][0]][t], e[k][1] == pi[g[l][1]][t]), And(e[k][1] == pi[g[l][0]][t], e[k][0] == pi[g[l][1]][t]))))

    for d in D:
        z3.add(time[d[0]] >= time[d[1]])

    for t in range(S - 1):
        for k in range(K):
            z3.add(sigma[k][t] == False)

    for t in range(S - 1, T):
        for k in range(K):
            for tt in range(t - S + 1, t + 1):
                for kk in O[k]:
                    z3.add(Implies(sigma[k][t] == True, sigma[kk][tt] == False))

    for t in range(T - 1):
        for n in range(N):
            for m in range(M):
                z3.add(Implies(And(sum([If(sigma[k][t], 1, 0) for k in edge_list[n]]) == 0, pi[m][t] == n), pi[m][t + 1] == n))

    for t in range(T - 1):
        for k in range(K):
            for m in range(M):
                z3.add(Implies(And(sigma[k][t] == True, pi[m][t] == e[k][0]), pi[m][t + 1] == e[k][1]))
                z3.add(Implies(And(sigma[k][t] == True, pi[m][t] == e[k][1]), pi[m][t + 1] == e[k][0]))

    #for c in z3.assertions():
    #    print(c)


# for area optimization
#    if objective_name == "swap":
    z3.add(num_swap == sum([If(sigma[k][t], 1, 0) for k in range(K) for t in range(T)]))


# for fidelity optimization
    if objective_name == "fidelity":
        for n in range(N):
            z3.add(u[n] == sum([If(space[l] == n, 1, 0) for l in G_1]))
            z3.add(w[n] == sum([If(pi[m][T - 1] == n, 1, 0) for m in range(M)]))
        for k in range(K):
            z3.add(v[k] == sum([If(space[l] == k, 1, 0) for l in G_2]))
            z3.add(vv[k] == sum([If(sigma[k][t], 1, 0) for t in range(T)]))

        z3.add(fidelity == sum([v[k] * f_2qbg[k] for k in range(K)]) +
                           sum([S * vv[k] * f_2qbg[k] for k in range(K)]) +
                           sum([w[n] * f_meas[n] for n in range(N)]) +
                           sum([u[n] * f_1qbg[n] for n in range(N)]))
        z3.maximize(fidelity)

# for depth optimization
    # else:
    for l in range(L):
        z3.add(depth >= time[l] + 1)
        # z3.minimize(depth)

    if objective_name == "swap":
        z3.minimize(num_swap)
    elif objective_name == "depth":
        ze.minimize(depth)

    satisfiable = z3.check()
    if satisfiable == sat:
        not_solve = False
    else:
        T += 1


print("Compilation time = {}.".format(sys_time.time() - start_time))
model = z3.model()
if objective_name == "fidelity":
    log_fidelity = model[fidelity].as_long()
    print("result fidelity = {}".format(math.exp(log_fidelity / 1000.0)))
    for k in range(K):
        tmp0 = model[v[k]].as_long()
        tmp1 = model[vv[k]].as_long()
        if (tmp0 != 0) or (tmp1 != 0):
            print("On edge {}, there are {} two-qubit gates and {} SWAP gates.".format(k, tmp0, tmp1))
    for n in range(N):
        tmp0 = model[u[n]].as_long()
        tmp1 = model[w[n]].as_long()
        if (tmp0 != 0) or (tmp1 != 0):
            print("On node {}, there are {} single-qubit gates and {} measurement.".format(n, tmp0, tmp1))
elif objective_name == "swap":
    print("result additional SWAP count = {}.".format(model[num_swap]))
else:
    print("result circuit depth = {}.".format(model[depth]))
result_depth = model[depth].as_long()


swap_list = list()
scheduled = [[] for i in range(result_depth)]
max_time = 0
for l in range(L):
    if model[time[l]].as_long() > max_time:
        max_time = model[time[l]].as_long()
    if l in G_1:
        print("gate {} is at cycle {} on node {}".format(l, model[time[l]], model[space[l]]))
        scheduled[model[time[l]].as_long()].append("{} q[{}];\n".format(gate_spec[l], model[space[l]]))
    elif l in G_2:
        k = model[space[l]].as_long()
        print("gate {} is at cycle {} on edge ({},{})".format(l, model[time[l]], e[k][0], e[k][1]))
        [q0, q1] = g[l]
        q0 = model[pi[q0][model[time[l]].as_long()]].as_long()
        q1 = model[pi[q1][model[time[l]].as_long()]].as_long()
        scheduled[model[time[l]].as_long()].append("{} q[{}], q[{}];\n".format(gate_spec[l], q0, q1))
for m in range(M):
    print("logical qubit {} is mapped to node {} in the beginning, node {} at the end".format(m, model[pi[m][0]], model[pi[m][result_depth - 1]]))
for k in range(K):
    for t in range(max_time + 1):
        if model[sigma[k][t]]:
            print("A swap gate finished at cycle {} on edge ({}, {}).".format(t, e[k][0], e[k][1]))
            scheduled[t].append("cx q[{}], q[{}]; // SWAP on edge {} at transition {}\n".format(e[k][0], e[k][1], k, t))
            scheduled[t].append("cx q[{}], q[{}]; // SWAP on edge {} at transition {}\n".format(e[k][1], e[k][0], k, t))
            scheduled[t].append("cx q[{}], q[{}]; // SWAP on edge {} at transition {}\n".format(e[k][0], e[k][1], k, t))

outFile = open(new_file_name + '.qasm', 'w')
outFile.write("// optimized for device {}\n".format(device_name))
outFile.writelines(['\n', "OPENQASM 2.0;\n", "include \"qelib1.inc\";\n", "qreg q[{}];\n".format(N), "creg c[{}];\n".format(M)])
for t in range(max_time + 1):
    outFile.writelines(['\n', "// cycle {}\n".format(t)])
    outFile.writelines(scheduled[t])
# outFile.writelines(['\n', "measure q -> c;\n"])
for m in range(M):
    outFile.write("measure q[{}] -> c[{}];\n".format(model[pi[m][max_time - 1]], m))
outFile.close()


qiskit_info_after(new_file_name + '.qasm', new_file_name, original_cx_count)
