from z3 import Int, IntVector, Bool, Optimize, Implies, And, Or, If, sat
from olsq.input import input_qasm
from olsq.output import output_qasm
import math


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


class OLSQ:
    def __init__(self, objective_name=None, mode=None):
        if objective_name is None:
            raise Exception("Please input objective name as the first argument: depth, swap, or fidelity.")
        elif objective_name == "depth":
            self.objective_name = objective_name
        elif objective_name == "swap":
            self.objective_name = objective_name
        elif objective_name == "fidelity":
            self.objective_name = objective_name
        else:
            raise Exception("Invalid Objective Name")

        if mode is None:
            raise Exception("Please select mode: nomral, transition")
        elif mode == "transition":
            self.if_transition_based = True
        elif mode == "normal":
            self.if_transition_based = False
        else:
            raise Exception("Invalid Choice of Transition-Based or Not")

        self.device = None
        self.list_gate_qubits = []
        self.count_program_qubit = 0
        self.list_gate_name = []
        self.count_physical_qubit = 0
        self.list_qubit_edge = []
        self.swap_duration = 0
        self.bound_depth = 0

    def setdevice(self, device=None):
        if device is None:
            raise Exception("no device")
        self.device = device
        self.count_physical_qubit = device.count_physical_qubit
        self.list_qubit_edge = device.list_qubit_edge
        self.swap_duration = device.swap_duration

    def setprogram(self, program=None, input_mode=None):
        if program is None:
            raise Exception("no input program")
        if input_mode == "IR":
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]
        else:
            program = input_qasm(program)
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]

        push_forward_depth = [0 for i in range(self.count_program_qubit)]
        for qubits in self.list_gate_qubits:
            if isinstance(qubits, int):
                push_forward_depth[qubits] += 1
            else:
                tmp_depth = push_forward_depth[qubits[0]]
                if tmp_depth < push_forward_depth[qubits[1]]:
                    tmp_depth = push_forward_depth[qubits[1]]
                push_forward_depth[qubits[1]] = tmp_depth + 1
                push_forward_depth[qubits[0]] = tmp_depth + 1
        self.bound_depth = max(push_forward_depth)

    def solve(self, output_mode=None, output_file_name=None):
        objective_name = self.objective_name

        device = self.device
        list_gate_qubits = self.list_gate_qubits
        count_program_qubit = self.count_program_qubit
        list_gate_name = self.list_gate_name
        count_physical_qubit = self.count_physical_qubit
        list_qubit_edge = self.list_qubit_edge
        swap_duration = self.swap_duration
        bound_depth = self.bound_depth

        """
        pre-processing
        """
        count_qubit_edge = len(list_qubit_edge)
        count_gate = len(list_gate_qubits)
        if self.objective_name == "fidelity":
            list_logfidelity_single = [int(1000 * math.log(device.list_fidelity_single[n]))
                                       for n in range(count_physical_qubit)]
            list_logfidelity_two = [int(1000 * math.log(device.list_fidelity_two[k]))
                                    for k in range(count_qubit_edge)]
            list_logfidelity_measure = [int(1000 * math.log(device.list_fidelity_measure[n]))
                                        for n in range(count_physical_qubit)]
        list_gate_two = list()
        list_gate_single = list()
        for l in range(count_gate):
            if isinstance(list_gate_qubits[l], int):
                list_gate_single.append(l)
            else:
                list_gate_two.append(l)

        # list_adjacency_qubit takes in a physical qubit index _p_, and returns the list of indices of
        # physical qubits adjacent to _p_
        list_adjacent_qubit = list()
        # list_span_edge takes in a physical qubit index _p_, and returns the list of edges spanned from _p_
        list_span_edge = list()
        for n in range(count_physical_qubit):
            list_adjacent_qubit.append(list())
            list_span_edge.append(list())
        for k in range(count_qubit_edge):
            list_adjacent_qubit[list_qubit_edge[k][0]].append(list_qubit_edge[k][1])
            list_adjacent_qubit[list_qubit_edge[k][1]].append(list_qubit_edge[k][0])
            list_span_edge[list_qubit_edge[k][0]].append(k)
            list_span_edge[list_qubit_edge[k][1]].append(k)

        # if_overlap_edge takes in two edge indices _e_ and _e'_, and returns whether or not they overlap
        if_overlap_edge = [[0] * count_qubit_edge for k in range(count_qubit_edge)]
        # list_over_lap_edge takes in an edge index _e_, and returns the list of edges that overlap with _e_
        list_overlap_edge = list()
        # list_count_overlap_edge is the list of lengths of overlap edge lists of all the _e_
        list_count_overlap_edge = list()
        for k in range(count_qubit_edge):
            list_overlap_edge.append(list())
        for k in range(count_qubit_edge):
            for kk in range(k + 1, count_qubit_edge):
                if (list_qubit_edge[k][0] == list_qubit_edge[kk][0]
                    or list_qubit_edge[k][0] == list_qubit_edge[kk][1]) \
                        or (list_qubit_edge[k][1] == list_qubit_edge[kk][0]
                            or list_qubit_edge[k][1] == list_qubit_edge[kk][1]):
                    list_overlap_edge[k].append(kk)
                    list_overlap_edge[kk].append(k)
                    if_overlap_edge[kk][k] = 1
                    if_overlap_edge[k][kk] = 1
        for k in range(count_qubit_edge):
            list_count_overlap_edge.append(len(list_overlap_edge[k]))

        # list_gate_dependency is the list of dependency, pairs of gate indices (_l_, _l'_), where _l_<_l'_
        # _l_ and _ll_ act on a same program qubit
        list_gate_dependency = dependency_extracting(list_gate_qubits)

        # index function: it takes two physical qubit indices _p_ and _p'_,
        # and returns the index of the edge between _p_ and _p'_, if there is one
        map_edge_index = [[0] * count_physical_qubit] * count_physical_qubit
        for k in range(count_qubit_edge):
            map_edge_index[list_qubit_edge[k][0]][list_qubit_edge[k][1]] = k
            map_edge_index[list_qubit_edge[k][1]][list_qubit_edge[k][0]] = k

        not_solved = True
        while not_solved:
            print("Trying maximal depth = {}...".format(bound_depth))

            """
            variables
            """

            # at cycle t, logical qubit q is mapped to pi[q][t]
            pi = [[Int("map_q{}_t{}".format(i, j)) for j in range(bound_depth)] for i in range(count_program_qubit)]

            # time coordinate for gate l is time[l]
            time = IntVector('time', count_gate)

            # space coordinate for gate l is space[l]
            space = IntVector('space', count_gate)

            # if at cycle t, there is a SWAP finishing on edge k, then sigma[k][t]=1
            sigma = [[Bool("ifswap_e{}_t{}".format(i, j)) for j in range(bound_depth)] for i in range(count_qubit_edge)]

            # for depth optimization
            depth = Int('depth')

            # for swap optimization
            count_swap = Int('num_swap')

            # for fidelity optimization
            if objective_name == "fidelity":
                u = [Int("num_1qbg_p{}".format(n)) for n in range(count_physical_qubit)]
                v = [Int("num_2qbg_e{}".format(k)) for k in range(count_qubit_edge)]
                vv = [Int("num_swap_e{}".format(k)) for k in range(count_qubit_edge)]
                w = [Int("num_meas_p{}".format(n)) for n in range(count_physical_qubit)]
                fidelity = Int('log_fidelity')

            lsqc = Optimize()

            """
            Constraints
            """

            for t in range(bound_depth):
                for m in range(count_program_qubit):
                    lsqc.add(pi[m][t] >= 0, pi[m][t] < count_physical_qubit)
                    for mm in range(m):
                        lsqc.add(pi[m][t] != pi[mm][t])

            for l in range(count_gate):
                lsqc.add(time[l] >= 0, time[l] < bound_depth)
                if l in list_gate_single:
                    lsqc.add(space[l] >= 0, space[l] < count_physical_qubit)
                    for t in range(bound_depth):
                        lsqc.add(Implies(time[l] == t, pi[list_gate_qubits[l]][t] == space[l]))
                elif l in list_gate_two:
                    lsqc.add(space[l] >= 0, space[l] < count_qubit_edge)
                    for k in range(count_qubit_edge):
                        for t in range(bound_depth):
                            lsqc.add(Implies(And(time[l] == t, space[l] == k),
                                             Or(And(list_qubit_edge[k][0] == pi[list_gate_qubits[l][0]][t],
                                                    list_qubit_edge[k][1] == pi[list_gate_qubits[l][1]][t]),
                                                And(list_qubit_edge[k][1] == pi[list_gate_qubits[l][0]][t],
                                                    list_qubit_edge[k][0] == pi[list_gate_qubits[l][1]][t]))))

            for d in list_gate_dependency:
                lsqc.add(time[d[0]] < time[d[1]])

            for t in range(swap_duration - 1):
                for k in range(count_qubit_edge):
                    lsqc.add(sigma[k][t] == False)

            for t in range(swap_duration - 1, bound_depth):
                for k in range(count_qubit_edge):
                    for tt in range(t - swap_duration + 1, t):
                        lsqc.add(Implies(sigma[k][t] == True, sigma[k][tt] == False))
                    for tt in range(t - swap_duration + 1, t + 1):
                        for kk in list_overlap_edge[k]:
                            lsqc.add(Implies(sigma[k][t] == True, sigma[kk][tt] == False))

            for t in range(swap_duration - 1, bound_depth):
                for k in range(count_qubit_edge):
                    for tt in range(t - swap_duration + 1, t + 1):
                        for l in range(count_gate):
                            if l in list_gate_single:
                                lsqc.add(Implies(And(time[l] == tt, Or(space[l] == list_qubit_edge[k][0],
                                                                       space[l] == list_qubit_edge[k][1])),
                                                 sigma[k][t] == False))
                            elif l in list_gate_two:
                                lsqc.add(Implies(And(time[l] == tt, space[l] == k), sigma[k][t] == False))
                                for kk in list_overlap_edge[k]:
                                    lsqc.add(Implies(And(time[l] == tt, space[l] == kk), sigma[k][t] == False))

            for t in range(bound_depth - 1):
                for n in range(count_physical_qubit):
                    for m in range(count_program_qubit):
                        lsqc.add(
                            Implies(And(sum([If(sigma[k][t], 1, 0) for k in list_span_edge[n]]) == 0, pi[m][t] == n),
                                    pi[m][t + 1] == n))

            for t in range(bound_depth - 1):
                for k in range(count_qubit_edge):
                    for m in range(count_program_qubit):
                        lsqc.add(Implies(And(sigma[k][t] == True, pi[m][t] == list_qubit_edge[k][0]),
                                         pi[m][t + 1] == list_qubit_edge[k][1]))
                        lsqc.add(Implies(And(sigma[k][t] == True, pi[m][t] == list_qubit_edge[k][1]),
                                         pi[m][t + 1] == list_qubit_edge[k][0]))

            lsqc.add(
                count_swap == sum([If(sigma[k][t], 1, 0) for k in range(count_qubit_edge) for t in range(bound_depth)]))

            # for depth optimization
            for l in range(count_gate):
                lsqc.add(depth >= time[l] + 1)

            if objective_name == "swap":
                lsqc.minimize(count_swap)
            elif objective_name == "depth":
                lsqc.minimize(depth)
            elif objective_name == "fidelity":
                for n in range(count_physical_qubit):
                    lsqc.add(u[n] == sum([If(space[l] == n, 1, 0) for l in list_gate_single]))
                    lsqc.add(w[n] == sum([If(pi[m][bound_depth - 1] == n, 1, 0) for m in range(count_program_qubit)]))
                for k in range(count_qubit_edge):
                    lsqc.add(v[k] == sum([If(space[l] == k, 1, 0) for l in list_gate_two]))
                    lsqc.add(vv[k] == sum([If(sigma[k][t], 1, 0) for t in range(bound_depth)]))

                lsqc.add(fidelity == sum([v[k] * list_logfidelity_two[k] for k in range(count_qubit_edge)]) +
                         sum([swap_duration * vv[k] * list_logfidelity_two[k] for k in range(count_qubit_edge)]) +
                         sum([w[n] * list_logfidelity_measure[n] for n in range(count_physical_qubit)]) +
                         sum([u[n] * list_logfidelity_single[n] for n in range(count_physical_qubit)]))
                lsqc.maximize(fidelity)
            else:
                raise Exception("Invalid Objective Name")

            satisfiable = lsqc.check()
            if satisfiable == sat:
                not_solved = False
            else:
                bound_depth = int(1.3 * bound_depth)

        # print("Compilation time = {}s.".format(sys_time.time() - start_time))
        model = lsqc.model()

        """
        post-processing
        """

        if objective_name == "fidelity":
            log_fidelity = model[fidelity].as_long()
            print("result fidelity = {}".format(math.exp(log_fidelity / 1000.0)))
        elif objective_name == "swap":
            print("result additional SWAP count = {}.".format(model[count_swap]))
        else:
            print("result circuit depth = {}.".format(model[depth]))
        result_depth = model[depth].as_long()

        list_scheduled_gate_qubits = [[] for i in range(result_depth)]
        list_scheduled_gate_name = [[] for i in range(result_depth)]
        result_depth = 0
        for l in range(count_gate):
            t = model[time[l]].as_long()
            if result_depth < t + 1:
                result_depth = t + 1

            list_scheduled_gate_name[t].append(list_gate_name[l])
            if l in list_gate_single:
                q = model[space[l]].as_long()
                list_scheduled_gate_qubits[t].append(q)
            elif l in list_gate_two:
                [q0, q1] = list_gate_qubits[l]
                q0 = model[pi[q0][t]].as_long()
                q1 = model[pi[q1][t]].as_long()
                list_scheduled_gate_qubits[t].append([q0, q1])
            else:
                raise Exception("Expect single- or two-qubit gate.")

        final_mapping = []
        for m in range(count_program_qubit):
            final_mapping.append(model[pi[m][result_depth - 1]].as_long())
            # print("logical qubit {} is mapped to node {} in the beginning, node {} at the end".format(
            #    m, model[pi[m][0]], model[pi[m][result_depth - 1]]))

        for k in range(count_qubit_edge):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    q0 = list_qubit_edge[k][0]
                    q1 = list_qubit_edge[k][1]
                    if self.swap_duration == 1:
                        list_scheduled_gate_qubits[t].append([q0, q1])
                        list_scheduled_gate_name[t].append("SWAP")
                    elif self.swap_duration == 3:
                        list_scheduled_gate_qubits[t].append([q0, q1])
                        list_scheduled_gate_name[t].append("cx")
                        list_scheduled_gate_qubits[t - 1].append([q1, q0])
                        list_scheduled_gate_name[t - 1].append("cx")
                        list_scheduled_gate_qubits[t - 2].append([q0, q1])
                        list_scheduled_gate_name[t - 2].append("cx")
                    else:
                        raise Exception("Expect SWAP duration one, or three (decomposed into CX gates)")

        if output_mode == "IR":
            if output_file_name:
                output_file = open(output_file_name, 'w')
                output_file.writelines([result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits,
                                        final_mapping])
            return [result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits, final_mapping]
        else:
            return output_qasm(self.device, result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits,
                               final_mapping, True, output_file_name)
