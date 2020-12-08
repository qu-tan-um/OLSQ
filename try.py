
from cirq import T, H, CNOT, Circuit, NamedQubit, GridQubit
import cirq.contrib.routing as ccr
q = [NamedQubit("q[{}]".format(i)) for i in range(3)]
circuit = Circuit(
    [[H(q[2])], [CNOT(q[1], q[2])], [T(q[2])**-1], [CNOT(q[0], q[2])],
     [T(q[2])], [CNOT(q[1], q[2])], [T(q[2])**-1], [CNOT(q[0], q[2])],
     [T(q[1]), T(q[2])], [CNOT(q[0], q[1]), H(q[2])],
     [T(q[0]), T(q[1])**-1], [CNOT(q[0], q[1])]]
)
print(circuit)
device = ["dev", 5, [(0, 1), (1, 2), (1, 3), (3, 4)], 3]

from olsq.olsq_cirq import OLSQ_cirq
lsqc_solver = OLSQ_cirq("depth", "transition")
lsqc_solver.setdevicegraph(ccr.gridqubits_to_graph_device([GridQubit(0, 0), GridQubit(0, 1), GridQubit(1, 0), GridQubit(1, 1)]))
lsqc_solver.setprogram(circuit)
circuit_new, mapping = lsqc_solver.solve()
print(circuit_new)


"""
from cirq import T, H, CNOT, Circuit, NamedQubit
from olsq import OLSQ
from olsq.device import qcdevice

lsqc_solver = OLSQ("depth", "normal")
circuit = "OPENQASM 2.0;\n include \"qelib1.inc\";\n qreg q[3];\n h q[2];\n cx q[1], q[2];\n tdg q[2];\n " \
          "cx q[0], q[2];\n t q[2];\n cx q[1], q[2];\n tdg q[2];\n cx q[0], q[2];\n t q[1];\n t q[2];\n " \
          "cx q[0], q[1];\n h q[2];\n t q[0];\n tdg q[1];\n cx q[0], q[1];\n"
lsqc_solver.setprogram(circuit)
lsqc_solver.setdevice(qcdevice("dev", 5, [(0, 1), (1, 2), (1, 3), (3, 4)], 3))
result = lsqc_solver.solve("/Users/bctan/Desktop/try.qasm")
print(result)
"""