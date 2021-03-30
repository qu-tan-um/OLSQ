import pytest
from qiskit import IBMQ
from qiskit import QuantumCircuit

from olsq.device import qcdevice
from olsq.olsq_qiskit import OLSQ_qiskit

circuit_str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[3];\nh q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[1];\nt q[2];\n" \
              "cx q[0], q[1];\nh q[2];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n"
circuit_qiskit = QuantumCircuit()
circuit_qiskit = circuit_qiskit.from_qasm_str(circuit_str)

device_tmp = qcdevice("ourense", 5, [(0, 1), (1, 2), (1, 3), (3, 4)], 3)

def test_olsq_depth_normal_devibm():
    lsqc_solver = OLSQ_qiskit("depth", "normal")

    provider = IBMQ.load_account()
    backend = provider.get_backend("ibmq_lima") # belem, quito also works
    lsqc_solver.setdevice(backend, "ibm")
    
    lsqc_solver.setprogram(circuit_qiskit)
    assert lsqc_solver.solve()[2] == 14

def test_olsq_swap_normal():
    lsqc_solver = OLSQ_qiskit("swap", "normal")
    lsqc_solver.setdevice(device_tmp)
    lsqc_solver.setprogram(circuit_qiskit)
    assert lsqc_solver.solve()[2] == 1

def test_olsq_depth_transition():
    lsqc_solver = OLSQ_qiskit("depth", "transition")
    lsqc_solver.setdevice(device_tmp)
    lsqc_solver.setprogram(circuit_qiskit)
    assert lsqc_solver.solve()[2] == 2

def test_olsq_swap_transition():
    lsqc_solver = OLSQ_qiskit("swap", "transition")
    lsqc_solver.setdevice(device_tmp)
    lsqc_solver.setprogram(circuit_qiskit)
    assert lsqc_solver.solve()[2] == 1
