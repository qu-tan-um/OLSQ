import pytest

from olsq.device import qcdevice
from olsq import OLSQ

circuit_str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[3];\nh q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[1];\nt q[2];\n" \
              "cx q[0], q[1];\nh q[2];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n"

circuit_file = open('olsq/benchmarks/toffoli.qasm', 'r').read()

device_tmp = qcdevice("ourense", 5, [(0, 1), (1, 2), (1, 3), (3, 4)], 3)

device_file = qcdevice("default_ourense")

def test_olsq_depth_normal_circstr_devtmp():
    lsqc_solver = OLSQ("depth", "normal")
    lsqc_solver.setprogram(circuit_str)
    lsqc_solver.setdevice(device_tmp)
    assert lsqc_solver.solve()[2] == 14

def test_olsq_swap_normal_circfile_devfile():
    lsqc_solver = OLSQ("swap", "normal")
    lsqc_solver.setprogram(circuit_file)
    lsqc_solver.setdevice(device_file)
    assert lsqc_solver.solve()[2] == 1

def test_olsq_depth_transition_circfile_devfile():
    lsqc_solver = OLSQ("depth", "transition")
    lsqc_solver.setprogram(circuit_file)
    lsqc_solver.setdevice(device_file)
    assert lsqc_solver.solve()[2] == 2

def test_olsq_swap_transition_circstr_devtmp():
    lsqc_solver = OLSQ("swap", "transition")
    lsqc_solver.setprogram(circuit_str)
    lsqc_solver.setdevice(device_tmp)
    assert lsqc_solver.solve()[2] == 1
