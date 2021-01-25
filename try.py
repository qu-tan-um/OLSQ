from olsq import OLSQ
from olsq.device import qcdevice

lsqc_solver = OLSQ("swap", "transition")
circuit = "OPENQASM 2.0;\n include \"qelib1.inc\";\n qreg q[3];\n h q[2];\n cx q[1], q[2];\n tdg q[2];\n " \
          "cx q[0], q[2];\n t q[2];\n cx q[1], q[2];\n tdg q[2];\n cx q[0], q[2];\n t q[1];\n t q[2];\n " \
          "cx q[0], q[1];\n h q[2];\n t q[0];\n tdg q[1];\n cx q[0], q[1];\n"
lsqc_solver.setprogram(circuit)
lsqc_solver.setdevice(qcdevice("dev", 5, [(0, 1), (1, 2), (1, 3), (3, 4)], 3))
result = lsqc_solver.solve()
print(result)
