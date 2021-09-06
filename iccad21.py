from post import compactify, push_left_layers
import argparse
import json

def get_mapping(count_qubits, program, edges, ifaltmatch):
    # from qiskit import QuantumCircuit
    # from qiskit.transpiler.passes import SabreLayout
    # from qiskit.transpiler import CouplingMap
    # from qiskit.converters import circuit_to_dag
    # from qiskit.circuit import Qubit, QuantumRegister
    # from random import shuffle, sample


    # circ = QuantumCircuit(count_qubits)
    # for gate in sample(program, len(program)):
    #     circ.cx(gate[0], gate[1])
    # dag_circ = circuit_to_dag(circ)
    # mapper = SabreLayout(CouplingMap(couplinglist=edges))
    # mapper.run(dag_circ)
    # layout = mapper.property_set["layout"].get_virtual_bits()
    # mapping = list()
    # for i in range(count_qubits):
    #     mapping.append(layout[Qubit(QuantumRegister(count_qubits, 'q'), i)])
    print("-------finding initial mapping-------------------------------")
    lsqc_solver = OLSQ("depth", "transition")
    lsqc_solver.setprogram([count_qubits, program,\
        ["ZZ" for i in range(len(program))]], input_mode="IR")
    lsqc_solver.setdevice( qcdevice(name="sycamore23", nqubits=23,\
        connection=edges, swap_duration=1), False)
    lsqc_solver.setcommutation([(0,1)],if_all_commute=True)
    result_depth, list_scheduled_gate_name, list_scheduled_gate_qubits,\
        initial_mapping, final_mapping, objective_value =\
            lsqc_solver.solve(output_mode="IR")

    print(initial_mapping)
    print("-------found initial mapping-------------------------------")
    return initial_mapping


graphs = {
    "8": [(0, 1), (0, 4), (0, 3), (1, 7), (1, 6), (2, 4), (2, 7), (2, 3),\
        (4, 6), (7, 5), (6, 5), (3, 5)], 
    "10": [(0, 1), (0, 3), (0, 8), (1, 2), (1, 5), (3, 8), (3, 5),\
        (8, 9), (2, 7), (2, 6), (7, 5), (7, 4), (4, 9), (4, 6), (9, 6)],
    "12": [(9, 10), (9, 0), (9, 8), (10, 7), (10, 3), (2, 4), (2, 6),\
        (2, 5), (4, 1), (4, 5), (1, 11), (1, 6), (11, 7), (11, 3),\
            (7, 8), (0, 6), (0, 8), (3, 5)],
    "14": [(4, 6), (4, 5), (4, 8), (6, 1), (6, 11), (5, 13), (5, 0),\
        (13, 8), (13, 1), (0, 1), (0, 3), (11, 10), (11, 3), (7, 10),\
            (7, 12), (7, 8), (10, 2), (3, 9), (9, 12), (9, 2), (2, 12)],
}

num_qubits = 23
edges = [
    (0, 2), (1, 2), (2, 3), (1, 5), (2, 6), (3, 7),
    (4, 5), (5, 6), (6, 7), (7, 8),
    (4, 10), (5, 11), (6, 12), (7, 13),
    (9, 10), (10, 11), (11, 12), (12, 13),
    (9, 15), (10, 16), (11, 17), (12, 18),
    (14, 15), (15, 16), (16, 17), (17, 18),
    (15, 19), (16, 20), (17, 21), (19, 20), (20, 21), (20, 22)]

from olsq import OLSQ
from olsq.device import qcdevice


# Initialize parser
parser = argparse.ArgumentParser()
# Adding optional argument
parser.add_argument("objective", metavar='OBJ', type=str,
    help="the objective: swap or depth")
parser.add_argument("benchmark", metavar='B', type=str,
    help="which input quantum circuit: qaoa, qv64, or sim5")
parser.add_argument("--size", dest="size", type=int,
    help="The size of the qaoa circuit: 8, 10, 12, or 14")
parser.add_argument("--matching", dest="ifaltmatch", action='store_true',
    help="if using alternating matchings")
parser.add_argument("--initmap", dest="ifinitmap", action='store_true',
    help="if setting initial mapping")
parser.add_argument("--filename", dest="filename", type=str,
    help="The file name of the results (a json dump)")
# Read arguments from command line
args = parser.parse_args()

lsqc_solver = OLSQ(args.objective, "normal")

if args.benchmark == "qaoa":
    lsqc_solver.setprogram([args.size, graphs[str(args.size)], \
        ["ZZ"] * len(graphs[str(args.size)]) ], input_mode="IR")
    lsqc_solver.setdevice( qcdevice(name="sycamore23", nqubits=23, \
        connection=edges, swap_duration=1), args.ifaltmatch)

    # the following line results in 'all gates are commutable'
    lsqc_solver.setcommutation([(0,1)], if_all_commute=True)
    if args.ifinitmap:
        lsqc_solver.setmapping(get_mapping(args.size,\
            graphs[str(args.size)], edges, args.ifaltmatch))

elif args.benchmark == "qv64":
    lsqc_solver.setprogram([6, [(0,1), (2,3), (4,5), (1,2), (4,5), (0,3),\
        (2,4), (0,1), (3,5), (1,2), (0,5), (3,4), (0,1), (2,5), (3,4),\
            (1,2), (0,3), (4,5)], ["SU(4)"] * 18 ], input_mode="IR")
    lsqc_solver.setdevice( qcdevice(name="linear6", nqubits=6,\
        connection=[(0,1), (1,2), (2,3), (3,4), (4,5)], swap_duration=1),\
            args.ifaltmatch)
    if args.ifinitmap:
        lsqc_solver.setmapping([0, 1, 2, 3, 4, 5])

elif args.benchmark == "sim5":
    lsqc_solver.setprogram([5, [(0,1), (0,2), (0,3), (0,4), (1,2), (1,3),\
        (1,4), (2,3), (2,4), (3,4)],  ["fsim"] * 10], input_mode="IR")
    # the following line results in 'all gates are commutable'
    lsqc_solver.setcommutation([(0,1)], if_all_commute=True)
    lsqc_solver.setdevice( qcdevice(name="linear5", nqubits=5,\
        connection=[(0,1), (1,2), (2,3), (3,4)], swap_duration=1),\
            args.ifaltmatch)
    if args.ifinitmap:
        lsqc_solver.setmapping([0, 1, 2, 3, 4])

else:
    raise ValueError("Invalid choice of benchmark.")


results = lsqc_solver.solve(output_mode="IR")
result_dict = {}
result_dict["result_depth"] = results[0]
result_dict["list_scheduled_gate_name"] = results[1]
result_dict["list_scheduled_gate_qubits"] = results[2]
result_dict["initial_mapping"] = results[3]
result_dict["final_mapping"] = results[4]
result_dict["objective_value"] = results[5]

# # use the following for removing useless swaps and compactify the circuit
# # However, this is not used for results in the paper.
# # qaoa_gate_qubits = list()
# # qaoa_gate_name = list()
# # for j in range(len(result_dict["list_scheduled_gate_qubits"])):
# #     qaoa_gate_qubits += result_dict["list_scheduled_gate_qubits"][j]
# #     for name in result_dict["list_scheduled_gate_name"][j]:
# #         if name == "excSWAP":
# #             qaoa_gate_name.append("swap")
# #         else:
# #             qaoa_gate_name.append(name)

# # result_qubits, result_specs = \
# #     compactify(qaoa_gate_qubits, qaoa_gate_name, edges, num_qubits)
# # depth, swap_count, layers_qubits, layers_specs = \
# #     push_left_layers(result_qubits, result_specs, num_qubits, True)
# # result_dict = {}
# # result_dict["depth"] = depth
# # result_dict["swap_count"] = swap_count
# # result_dict["layers_qubits"] = layers_qubits
# # result_dict["layers_specs"] = layers_specs

outfile = open(args.filename+'.json', 'w')
json.dump(result_dict, outfile)
outfile.close()
