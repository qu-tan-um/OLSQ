import math
import datetime

from z3 import Int, IntVector, Bool, Optimize, Implies, And, Or, If, sat

from olsq.input import input_qasm
from olsq.output import output_qasm
from olsq.device import qcdevice
import pkgutil


def collision_extracting(list_gate_qubits):
    """Extract collision relations between the gates,
    If two gates g_1 and g_2 both acts on a qubit (at different time),
    we say that g_1 and g_2 collide on that qubit, which means that
    (1,2) will be in collision list.

    Args:
        list_gate_qubits: a list of gates in OLSQ IR
    
    Returns:
        list_collision: a list of collisions between the gates
    """

    list_collision = list()
    # We sweep through all the gates.  For each gate, we sweep through all the
    # gates after it, if they both act on some qubit, append them in the list.
    for g in range(len(list_gate_qubits)):
        for gg in range(g + 1, len(list_gate_qubits)):
            
            if list_gate_qubits[g][0] == list_gate_qubits[gg][0]:
                    list_collision.append((g, gg))
                
            if len(list_gate_qubits[gg]) == 2:
                if list_gate_qubits[g][0] == list_gate_qubits[gg][1]:
                    list_collision.append((g, gg))
            
            if len(list_gate_qubits[g]) == 2:
                if list_gate_qubits[g][1] == list_gate_qubits[gg][0]:
                    list_collision.append((g, gg))
                if len(list_gate_qubits[gg]) == 2:
                    if list_gate_qubits[g][1] == list_gate_qubits[gg][1]:
                        list_collision.append((g, gg))
    
    return tuple(list_collision)

def dependency_extracting(list_gate_qubits, count_program_qubit: int):
    """Extract dependency relations between the gates.
    If two gates g_1 and g_2 both acts on a qubit *and there is no gate
    between g_1 and g_2 that act on this qubit*, we then say that
    g2 depends on g1, which means that (1,2) will be in dependency list.

    Args:
        list_gate_qubits: a list of gates in OLSQ IR
        count_program_qubit: the number of logical/program qubit
    
    Returns:
        list_dependency: a list of dependency between the gates
    """

    list_dependency = []
    list_last_gate = [-1 for i in range(count_program_qubit)]
    # list_last_gate records the latest gate that acts on each qubit.
    # When we sweep through all the gates, this list is updated and the
    # dependencies induced by the update is noted.
    for i, qubits in enumerate(list_gate_qubits):
        
        if list_last_gate[qubits[0]] >= 0:
            list_dependency.append((list_last_gate[qubits[0]], i))
        list_last_gate[qubits[0]] = i

        if len(qubits) == 2:
            if list_last_gate[qubits[1]] >= 0:
                list_dependency.append((list_last_gate[qubits[1]], i))
            list_last_gate[qubits[1]] = i

    return tuple(list_dependency)


class OLSQ:
    def __init__(self, objective_name, mode):
        """Set the objective of OLSQ, and whether it is transition-based

        Args:
            objective_name: can be "depth", "swap", or "fidelity"
            mode: can be "normal" or "transition" (TB-OLSQ in the paper)       
        """
        
        if objective_name == "depth":
            self.objective_name = objective_name
        elif objective_name == "swap":
            self.objective_name = objective_name
        elif objective_name == "fidelity":
            self.objective_name = objective_name
        else:
            raise ValueError("Invalid Objective Name")

        if mode == "transition":
            self.if_transition_based = True
        elif mode == "normal":
            self.if_transition_based = False
        else:
            raise ValueError("Invalid Choice of Transition-Based or Not")

        # These values should be updated in setdevice(...)
        self.device = None
        self.count_physical_qubit = 0
        self.list_qubit_edge = []
        self.swap_duration = 0

        # These values should be updated in setprogram(...)
        self.list_gate_qubits = []
        self.count_program_qubit = 0
        self.list_gate_name = []
        
        # bound_depth is a hyperparameter
        self.bound_depth = 0

        self.inpput_dependency = False
        self.list_gate_dependency = []

    def setdevice(self, device: qcdevice):
        """Pass in parameters from the given device.  If in TB mode,
           swap_duration is set to 1 without modifying the device.

        Args:
            device: a qcdevice object for OLSQ
        """

        self.device = device
        self.count_physical_qubit = device.count_physical_qubit
        self.list_qubit_edge = device.list_qubit_edge
        self.swap_duration = device.swap_duration
        if self.if_transition_based:
            self.swap_duration = 1

    def setprogram(self, program, input_mode: str = None):
        """Translate input program to OLSQ IR, and set initial depth
        An example of the intermediate representation is shown below.
        It contains three things: 1) the number of qubit in the program,
        2) a list of tuples representing qubit(s) acted on by a gate,
        the tuple has one index if it is a single-qubit gate,
        two indices if it is a two-qubit gate, and 3) a list of
        type/name of each gate, which is not important to OLSQ,
        and only needed when generating output.
        If in TB mode, initial depth=1; in normal mode, we perform ASAP
        scheduling without consideration of SWAP to calculate depth.

        Args:
            program: a qasm string, or a list of the three things in IR.
            input_mode: (optional) can be "IR" if the input has ben
                translated to OLSQ IR; can be "benchmark" to use one of
                the benchmarks.  Default mode assumes qasm input.

        Example:
            For the following circuit
                q_0: ───────────────────■───
                                        │  
                q_1: ───────■───────────┼───
                     ┌───┐┌─┴─┐┌─────┐┌─┴─┐
                q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
                     └───┘└───┘└─────┘└───┘ 
            count_program_qubit = 3
            gates = ((2,), (1,2), (2,), (0,1))
            gate_spec = ("h", "cx", "tdg", "cx")
        """
        
        if input_mode == "IR":
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]
        elif input_mode == "benchmark":
            f = pkgutil.get_data(__name__, "benchmarks/" + program + ".qasm")
            program = input_qasm(f.decode("utf-8"))
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]
        else:
            program = input_qasm(program)
            self.count_program_qubit = program[0]
            self.list_gate_qubits = program[1]
            self.list_gate_name = program[2]

        # calculate the initial depth
        if self.if_transition_based:
            self.bound_depth = 1
        else:
            push_forward_depth = [0 for i in range(self.count_program_qubit)]
            for qubits in self.list_gate_qubits:
                if len(qubits) == 1:
                    push_forward_depth[qubits[0]] += 1
                else:
                    tmp_depth = push_forward_depth[qubits[0]]
                    if tmp_depth < push_forward_depth[qubits[1]]:
                        tmp_depth = push_forward_depth[qubits[1]]
                    push_forward_depth[qubits[1]] = tmp_depth + 1
                    push_forward_depth[qubits[0]] = tmp_depth + 1
            self.bound_depth = max(push_forward_depth)

    def setdependency(self, dependency: list):
        """Specify dependency (non-commutation)

        Args:
            dependency: a list of gate index pairs
        
        Example:
            For the following circuit
                q_0: ───────────────────■───
                                        │  
                q_1: ───────■───────────┼───
                     ┌───┐┌─┴─┐┌─────┐┌─┴─┐
                q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
                     └───┘└───┘└─────┘└───┘ 
                gate   0    1     2     3
            dependency = [(0,1), (1,2), (2,3)]

            However, for this QAOA subcircuit (ZZ gates may have phase
            parameters, but we neglect them for simplicity here)
                         ┌──┐ ┌──┐
                q_0: ────┤ZZ├─┤  ├─
                     ┌──┐└┬─┘ │ZZ│  
                q_1: ┤  ├─┼───┤  ├─
                     │ZZ│┌┴─┐ └──┘
                q_2: ┤  ├┤ZZ├──────
                     └──┘└──┘ 
                gate   0   1   2
            dependency = []    # since ZZ gates are commutable
        """
        self.list_gate_dependency = dependency
        self.inpput_dependency = True

    def solve(self, output_mode: str = None, output_file_name: str = None):
        """Formulate an SMT, pass it to z3 solver, and output results.
        CORE OF OLSQ, EDIT WITH CARE.

        Args:
            output_mode: "IR" or left to default.
            output_file_name: a file to store the IR output or qasm.
        
        Returns:
            a list of results depending on output_mode
            "IR": 
            | list_scheduled_gate_name: name/type of each gate
            | list_scheduled_gate_qubits: qubit(s) each gate acts on
            | final_mapping: logical qubit |-> physical qubit in the end 
            | objective_value: depth/#swap/fidelity depending on setting
            None:
              a qasm string
              final_mapping
              objective_value
        """

        objective_name = self.objective_name
        device = self.device
        list_gate_qubits = self.list_gate_qubits
        count_program_qubit = self.count_program_qubit
        list_gate_name = self.list_gate_name
        count_physical_qubit = self.count_physical_qubit
        list_qubit_edge = self.list_qubit_edge
        swap_duration = self.swap_duration
        bound_depth = self.bound_depth

        # pre-processing

        count_qubit_edge = len(list_qubit_edge)
        count_gate = len(list_gate_qubits)
        if self.objective_name == "fidelity":
            list_logfidelity_single = [
                int(1000 * math.log(device.list_fidelity_single[n]))
                for n in range(count_physical_qubit)]
            list_logfidelity_two = [
                int(1000 * math.log(device.list_fidelity_two[k]))
                for k in range(count_qubit_edge)]
            list_logfidelity_measure = [
                int(1000 * math.log(device.list_fidelity_measure[n]))
                for n in range(count_physical_qubit)]
        list_gate_two = list()
        list_gate_single = list()
        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                list_gate_single.append(l)
            else:
                list_gate_two.append(l)

        # list_adjacency_qubit takes in a physical qubit index _p_, and
        # returns the list of indices of physical qubits adjacent to _p_
        list_adjacent_qubit = list()
        # list_span_edge takes in a physical qubit index _p_,
        # and returns the list of edges spanned from _p_
        list_span_edge = list()
        for n in range(count_physical_qubit):
            list_adjacent_qubit.append(list())
            list_span_edge.append(list())
        for k in range(count_qubit_edge):
            list_adjacent_qubit[list_qubit_edge[k][0]].append(
                                                        list_qubit_edge[k][1])
            list_adjacent_qubit[list_qubit_edge[k][1]].append(
                                                        list_qubit_edge[k][0])
            list_span_edge[list_qubit_edge[k][0]].append(k)
            list_span_edge[list_qubit_edge[k][1]].append(k)

        # if_overlap_edge takes in two edge indices _e_ and _e'_,
        # and returns whether or not they overlap
        if_overlap_edge = [[0] * count_qubit_edge
            for k in range(count_qubit_edge)]
        # list_over_lap_edge takes in an edge index _e_,
        # and returnsthe list of edges that overlap with _e_
        list_overlap_edge = list()
        # list_count_overlap_edge is the list of lengths of
        # overlap edge lists of all the _e_
        list_count_overlap_edge = list()
        for k in range(count_qubit_edge):
            list_overlap_edge.append(list())
        for k in range(count_qubit_edge):
            for kk in range(k + 1, count_qubit_edge):
                if (   (list_qubit_edge[k][0] == list_qubit_edge[kk][0]
                        or list_qubit_edge[k][0] == list_qubit_edge[kk][1])
                    or (list_qubit_edge[k][1] == list_qubit_edge[kk][0]
                        or list_qubit_edge[k][1] == list_qubit_edge[kk][1]) ):
                    list_overlap_edge[k].append(kk)
                    list_overlap_edge[kk].append(k)
                    if_overlap_edge[kk][k] = 1
                    if_overlap_edge[k][kk] = 1
        for k in range(count_qubit_edge):
            list_count_overlap_edge.append(len(list_overlap_edge[k]))

        if not self.inpput_dependency:
            list_gate_dependency = collision_extracting(list_gate_qubits)
        else:
            list_gate_dependency = self.list_gate_dependency

        # index function: takes two physical qubit indices _p_ and _p'_,
        # and returns the index of the edge between them if there is one
        map_edge_index = [[0] * count_physical_qubit] * count_physical_qubit
        for k in range(count_qubit_edge):
            map_edge_index[list_qubit_edge[k][0]][list_qubit_edge[k][1]] = k
            map_edge_index[list_qubit_edge[k][1]][list_qubit_edge[k][0]] = k

        not_solved = True
        start_time = datetime.datetime.now()
        while not_solved:
            print("Trying maximal depth = {}...".format(bound_depth))

            # variable setting 

            # at cycle t, logical qubit q is mapped to pi[q][t]
            pi = [[Int("map_q{}_t{}".format(i, j)) for j in range(bound_depth)]
                  for i in range(count_program_qubit)]

            # time coordinate for gate l is time[l]
            time = IntVector('time', count_gate)

            # space coordinate for gate l is space[l]
            space = IntVector('space', count_gate)

            # if at cycle t, a SWAP finishing on edge k, then sigma[k][t]=1
            sigma = [[Bool("ifswap_e{}_t{}".format(i, j))
                for j in range(bound_depth)] for i in range(count_qubit_edge)]

            # for depth optimization
            depth = Int('depth')

            # for swap optimization
            count_swap = Int('num_swap')

            # for fidelity optimization
            if objective_name == "fidelity":
                u = [Int("num_1qbg_p{}".format(n))
                     for n in range(count_physical_qubit)]
                v = [Int("num_2qbg_e{}".format(k))
                     for k in range(count_qubit_edge)]
                vv = [Int("num_swap_e{}".format(k))
                      for k in range(count_qubit_edge)]
                w = [Int("num_meas_p{}".format(n))
                     for n in range(count_physical_qubit)]
                fidelity = Int('log_fidelity')

            lsqc = Optimize()

            # constraint setting

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
                        lsqc.add(Implies(time[l] == t,
                            pi[list_gate_qubits[l][0]][t] == space[l]))
                elif l in list_gate_two:
                    lsqc.add(space[l] >= 0, space[l] < count_qubit_edge)
                    for k in range(count_qubit_edge):
                        for t in range(bound_depth):
                            lsqc.add(Implies(And(time[l] == t, space[l] == k),
                                Or(And(list_qubit_edge[k][0] == \
                                        pi[list_gate_qubits[l][0]][t],
                                    list_qubit_edge[k][1] == \
                                        pi[list_gate_qubits[l][1]][t]),
                                And(list_qubit_edge[k][1] == \
                                        pi[list_gate_qubits[l][0]][t],
                                    list_qubit_edge[k][0] == \
                                        pi[list_gate_qubits[l][1]][t])  )    ))

            for d in list_gate_dependency:
                if self.if_transition_based:
                    lsqc.add(time[d[0]] <= time[d[1]])
                else:
                    lsqc.add(time[d[0]] < time[d[1]])

            for t in range(min(swap_duration - 1, bound_depth)):
                for k in range(count_qubit_edge):
                    lsqc.add(sigma[k][t] == False)

            for t in range(swap_duration - 1, bound_depth):
                for k in range(count_qubit_edge):
                    for tt in range(t - swap_duration + 1, t):
                        lsqc.add(Implies(sigma[k][t] == True,
                            sigma[k][tt] == False))
                    for tt in range(t - swap_duration + 1, t + 1):
                        for kk in list_overlap_edge[k]:
                            lsqc.add(Implies(sigma[k][t] == True,
                                sigma[kk][tt] == False))

            if not self.if_transition_based:
                for t in range(swap_duration - 1, bound_depth):
                    for k in range(count_qubit_edge):
                        for tt in range(t - swap_duration + 1, t + 1):
                            for l in range(count_gate):
                                if l in list_gate_single:
                                    lsqc.add(Implies(And(time[l] == tt,
                                        Or(space[l] == list_qubit_edge[k][0],
                                           space[l] == list_qubit_edge[k][1])),
                                            sigma[k][t] == False             ))
                                elif l in list_gate_two:
                                    lsqc.add(Implies(And(
                                        time[l] == tt, space[l] == k),
                                            sigma[k][t] == False           ))
                                    for kk in list_overlap_edge[k]:
                                        lsqc.add(Implies(And(
                                            time[l] == tt, space[l] == kk),
                                                sigma[k][t] == False       ))

            for t in range(bound_depth - 1):
                for n in range(count_physical_qubit):
                    for m in range(count_program_qubit):
                        lsqc.add(
                            Implies(And(sum([If(sigma[k][t], 1, 0)
                                for k in list_span_edge[n]]) == 0,
                                    pi[m][t] == n), pi[m][t + 1] == n))

            for t in range(bound_depth - 1):
                for k in range(count_qubit_edge):
                    for m in range(count_program_qubit):
                        lsqc.add(Implies(And(sigma[k][t] == True,
                            pi[m][t] == list_qubit_edge[k][0]),
                                pi[m][t + 1] == list_qubit_edge[k][1]))
                        lsqc.add(Implies(And(sigma[k][t] == True,
                            pi[m][t] == list_qubit_edge[k][1]),
                                pi[m][t + 1] == list_qubit_edge[k][0]))

            lsqc.add(
                count_swap == sum([If(sigma[k][t], 1, 0)
                    for k in range(count_qubit_edge)
                        for t in range(bound_depth)]))

            # for depth optimization
            for l in range(count_gate):
                lsqc.add(depth >= time[l] + 1)

            if objective_name == "swap":
                lsqc.minimize(count_swap)
            elif objective_name == "depth":
                lsqc.minimize(depth)
            elif objective_name == "fidelity":
                for n in range(count_physical_qubit):
                    lsqc.add(u[n] == sum([If(space[l] == n, 1, 0)
                        for l in list_gate_single]))
                    lsqc.add(w[n] == sum([If(pi[m][bound_depth - 1] == n, 1, 0)
                        for m in range(count_program_qubit)]))
                for k in range(count_qubit_edge):
                    lsqc.add(v[k] == sum([If(space[l] == k, 1, 0)
                        for l in list_gate_two]))
                    lsqc.add(vv[k] == sum([If(sigma[k][t], 1, 0)
                        for t in range(bound_depth)]))

                lsqc.add(fidelity == sum([v[k] * list_logfidelity_two[k]
                    for k in range(count_qubit_edge)])
                    + sum([
                        swap_duration * vv[k] * list_logfidelity_two[k]
                        for k in range(count_qubit_edge)])
                    + sum([w[n] * list_logfidelity_measure[n]
                        for n in range(count_physical_qubit)])
                    + sum([u[n] * list_logfidelity_single[n]
                        for n in range(count_physical_qubit)])          )
                lsqc.maximize(fidelity)
            else:
                raise Exception("Invalid Objective Name")

            satisfiable = lsqc.check()
            if satisfiable == sat:
                not_solved = False
            else:
                if self.if_transition_based:
                    bound_depth += 1
                else:
                    bound_depth = int(1.3 * bound_depth)

        print(f"Compilation time = {datetime.datetime.now() - start_time}.")
        model = lsqc.model()

        # post-processing

        result_time = []
        result_depth = model[depth].as_long()
        for l in range(count_gate):
            result_time.append(model[time[l]].as_long())
        list_result_swap = []
        for k in range(count_qubit_edge):
            for t in range(result_depth):
                if model[sigma[k][t]]:
                    list_result_swap.append((k, t))
                    print(f"SWAP on physical edge ({list_qubit_edge[k][0]},"\
                        + f"{list_qubit_edge[k][1]}) at time {t}")
        for l in range(count_gate):
            if len(list_gate_qubits[l]) == 1:
                qq = list_gate_qubits[l][0]
                tt = result_time[l]
                print(f"Gate {l}: {list_gate_name[l]} {qq} on qubit "\
                    + f"{model[pi[qq][tt]].as_long()} at time {tt}")
            else:
                qq = list_gate_qubits[l][0]
                qqq = list_gate_qubits[l][1]
                tt = result_time[l]
                print(f"Gate {l}: {list_gate_name[l]} {qq}, {qqq} on qubits "\
                    + f"{model[pi[qq][tt]].as_long()} and "\
                    + f"{model[pi[qqq][tt]].as_long()} at time {tt}")


        # transition based
        if self.if_transition_based:
            self.swap_duration = self.device.swap_duration
            real_time = [0 for i in range(count_gate)]
            list_depth_on_qubit = [-1 for i in range(self.count_physical_qubit)]
            list_real_swap = []
            for block in range(result_depth):
                for tmp_gate in range(count_gate):
                    if result_time[tmp_gate] == block:
                        qubits = list_gate_qubits[tmp_gate]
                        if len(qubits) == 1:
                            p0 = model[pi[qubits[0]][block]].as_long()
                            real_time[tmp_gate] = \
                                list_depth_on_qubit[p0] + 1
                            list_depth_on_qubit[p0] = \
                                real_time[tmp_gate]
                        else:
                            p0 = model[pi[qubits[0]][block]].as_long()
                            p1 = model[pi[qubits[1]][block]].as_long()
                            real_time[tmp_gate] = max(
                                list_depth_on_qubit[p0],
                                list_depth_on_qubit[p1]) + 1
                            list_depth_on_qubit[p0] = \
                                real_time[tmp_gate]
                            list_depth_on_qubit[p1] = \
                                real_time[tmp_gate]
                            # print(f"{tmp_gate} {p0} {p1} real-time={real_time[tmp_gate]}")

                if block < result_depth - 1:
                    for (k, t) in list_result_swap:
                        if t == block:
                            p0 = list_qubit_edge[k][0]
                            p1 = list_qubit_edge[k][1]
                            tmp_time = max(list_depth_on_qubit[p0],
                                list_depth_on_qubit[p1]) \
                                + self.swap_duration
                            list_depth_on_qubit[p0] = tmp_time
                            list_depth_on_qubit[p1] = tmp_time
                            list_real_swap.append((k, tmp_time))
                # print(list_depth_on_qubit)
            result_time = real_time
            real_depth = 0
            for tmp_depth in list_depth_on_qubit:
                if real_depth < tmp_depth + 1:
                    real_depth = tmp_depth + 1
            result_depth = real_depth
            list_result_swap = list_real_swap
            # print(list_result_swap)
        
        objective_value = 0
        if objective_name == "fidelity":
            objective_value = model[fidelity].as_long()
            print(f"result fidelity = {math.exp(objective_value / 1000.0)}")
        elif objective_name == "swap":
            objective_value = len(list_result_swap)
            print(f"result additional SWAP count = {objective_value}.")
        else:
            objective_value = model[depth].as_long()
            print(f"result circuit depth = {objective_value}.")

        list_scheduled_gate_qubits = [[] for i in range(result_depth)]
        list_scheduled_gate_name = [[] for i in range(result_depth)]
        result_depth = 0
        for l in range(count_gate):
            t = result_time[l]

            if result_depth < t + 1:
                result_depth = t + 1

            list_scheduled_gate_name[t].append(list_gate_name[l])
            if l in list_gate_single:
                q = model[space[l]].as_long()
                list_scheduled_gate_qubits[t].append((q,))
            elif l in list_gate_two:
                [q0, q1] = list_gate_qubits[l]
                tmp_t = t
                if self.if_transition_based:
                    tmp_t = model[time[l]].as_long()
                q0 = model[pi[q0][tmp_t]].as_long()
                q1 = model[pi[q1][tmp_t]].as_long()
                list_scheduled_gate_qubits[t].append((q0, q1))
            else:
                raise ValueError("Expect single-qubit or two-qubit gate.")

        final_mapping = []
        for m in range(count_program_qubit):
            tmp_depth = result_depth - 1
            if self.if_transition_based:
                tmp_depth = model[depth].as_long() - 1
            final_mapping.append(model[pi[m][tmp_depth]].as_long())

        for (k, t) in list_result_swap:
            q0 = list_qubit_edge[k][0]
            q1 = list_qubit_edge[k][1]
            if self.swap_duration == 1:
                list_scheduled_gate_qubits[t].append((q0, q1))
                list_scheduled_gate_name[t].append("SWAP")
            elif self.swap_duration == 3:
                list_scheduled_gate_qubits[t].append((q0, q1))
                list_scheduled_gate_name[t].append("cx")
                list_scheduled_gate_qubits[t - 1].append((q1, q0))
                list_scheduled_gate_name[t - 1].append("cx")
                list_scheduled_gate_qubits[t - 2].append((q0, q1))
                list_scheduled_gate_name[t - 2].append("cx")
            else:
                raise ValueError("Expect SWAP duration one, or three")

        if output_mode == "IR":
            if output_file_name:
                output_file = open(output_file_name, 'w')
                output_file.writelines([list_scheduled_gate_name,
                                        list_scheduled_gate_qubits,
                                        final_mapping,
                                        objective_value])
            return (result_depth,
                    list_scheduled_gate_name,
                    list_scheduled_gate_qubits,
                    final_mapping,
                    objective_value)
        else:
            return (output_qasm(device, result_depth, list_scheduled_gate_name,
                                list_scheduled_gate_qubits, final_mapping,
                                True, output_file_name),
                    final_mapping,
                    objective_value)
