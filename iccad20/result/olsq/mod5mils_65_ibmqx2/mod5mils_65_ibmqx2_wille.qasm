
// 0->1, 1->4, 2->3, 3->2, 4->0
OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[5];
cx q[4], q[2];
x q[2];
h q[0];
t q[2];
t q[1];
t q[0];
cx q[1], q[2];
cx q[0], q[1];
cx q[2], q[0];
tdg q[1];
cx q[2], q[1];
tdg q[2];
tdg q[1];
t q[0];
cx q[0], q[1];
cx q[2], q[1]; // swap 1 2
cx q[1], q[2]; // swap 1 2
cx q[2], q[1]; // swap 1 2

// 0->2, 1->4, 2->3, 3->1, 4->0
cx q[1], q[0];
cx q[2], q[1];
cx q[2], q[3]; // swap 2 3
cx q[3], q[2]; // swap 2 3
cx q[2], q[3]; // swap 2 3

// 0->3, 1->4, 2->2, 3->1, 4->0
h q[0];
h q[0];
t q[1];
t q[2];
t q[0];
cx q[2], q[1];
cx q[0], q[2];
cx q[1], q[0];
tdg q[2];
cx q[1], q[2];
tdg q[1];
tdg q[2];
t q[0];
cx q[0], q[2];
cx q[1], q[0];
cx q[2], q[1];
h q[0];
cx q[1], q[0];

measure q[3]->c[0];
measure q[4]->c[1];
measure q[3]->c[2];
measure q[1]->c[3];
measure q[0]->c[4];
