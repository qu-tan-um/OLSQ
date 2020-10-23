import networkx as nx
from smt_qaoa import qaoa_exp_smt
import pytket
import cirq
from pytket.cirq import tk_to_cirq
from pytket.routing import route, Architecture
from pytket.transform import Transform
import sys


M = int(sys.argv[1])
graph = nx.random_regular_graph(3, M)
edges = list(graph.edges())
print(edges)

connection_list = [(0, 2), (1, 2), (2, 3), (1, 5), (2, 6), (3, 7),
                                    (4, 5), (5, 6), (6, 7), (7, 8),
                                    (4, 10), (5, 11), (6, 12), (7, 13),
                                    (9, 10), (10, 11), (11, 12), (12, 13),
                                    (9, 15), (10, 16), (11, 17), (12, 18),
                                    (14, 15), (15, 16), (16, 17), (17, 18),
                                    (15, 19), (16, 20), (17, 21), (19, 20), (20, 21), (20, 22)]



circ = pytket.Circuit(23, 0)
for edge in edges:
    circ.ZZPhase(angle=0.75, qubit0=edge[0], qubit1=edge[1])

routed_circ = route(circ, Architecture(connection_list), decompose_swaps=False)
Transform.DecomposeBRIDGE().apply(routed_circ)

cirq_circuit = tk_to_cirq(routed_circ)
num_swap = 0
for layer in cirq_circuit:
    for gate in layer:
        if gate.__str__().startswith('SWAP'):
            num_swap += 1
tket_depth = len(cirq_circuit)
print("num_swap", num_swap, " depth", tket_depth)
for layer in cirq_circuit:
    print(layer)

[our_depth, our_swap] = qaoa_exp_smt(M, edges)

with open('result', 'a') as file:
    file.write(str(M) + '\n')
    file.write(str(edges) + '\n')
    file.write('tket depth ' + str(tket_depth) + ' SWAP ' + str(num_swap) + '\n')
    file.write('our depth ' + str(our_depth) + ' SWAP ' + str(our_swap) + '\n\n')
file.close()
