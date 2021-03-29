import pytest
import networkx
from cirq.contrib.qasm_import import circuit_from_qasm
from cirq import NamedQubit

from olsq.device import qcdevice
from olsq.olsq_cirq import OLSQ_cirq

circuit = circuit_from_qasm("""OPENQASM 2.0;
                               include "qelib1.inc";
                               qreg q[3];
                               h q[2];
                               cx q[1], q[2];
                               tdg q[2];
                               cx q[0], q[2];
                               t q[2];
                               cx q[1], q[2];
                               tdg q[2];
                               cx q[0], q[2];
                               t q[1];
                               t q[2];
                               cx q[0], q[1];
                               h q[2];
                               t q[0];
                               tdg q[1];
                               cx q[0], q[1];""")

device_graph = networkx.Graph()
device_graph.add_nodes_from([NamedQubit(f'q_{i}') for i in range(5)])
device_graph.add_edge(NamedQubit('q_0'), NamedQubit('q_1'))
device_graph.add_edge(NamedQubit('q_1'), NamedQubit('q_2'))
device_graph.add_edge(NamedQubit('q_1'), NamedQubit('q_3'))
device_graph.add_edge(NamedQubit('q_3'), NamedQubit('q_4'))

def test_olsq_depth_normal():
    lsqc_solver = OLSQ_cirq("depth", "normal")
    lsqc_solver.setdevicegraph(device_graph)
    lsqc_solver.setprogram(circuit)
    assert lsqc_solver.solve()[2] == 14

def test_olsq_swap_normal():
    lsqc_solver = OLSQ_cirq("swap", "normal")
    lsqc_solver.setdevicegraph(device_graph)
    lsqc_solver.setprogram(circuit)
    assert lsqc_solver.solve()[2] == 1

def test_olsq_depth_transition():
    lsqc_solver = OLSQ_cirq("depth", "transition")
    lsqc_solver.setdevicegraph(device_graph)
    lsqc_solver.setprogram(circuit)
    assert lsqc_solver.solve()[2] == 2

def test_olsq_swap_transition():
    lsqc_solver = OLSQ_cirq("swap", "transition")
    lsqc_solver.setdevicegraph(device_graph)
    lsqc_solver.setprogram(circuit)
    assert lsqc_solver.solve()[2] == 1
