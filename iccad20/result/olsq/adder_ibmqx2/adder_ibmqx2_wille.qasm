OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[4];
// 0->2, 1->1, 2->3, 3->4
x q[2];
x q[1];
h q[3];
cx q[3], q[4];
t q[2];
t q[1];
t q[3];
tdg q[4];
cx q[2], q[1];
cx q[3], q[4];

cx q[2], q[3]; //swap 2 3
cx q[3], q[2]; //swap 2 3
cx q[2], q[3]; //swap 2 3
// 0->3, 1->1, 2->2, 3->4
cx q[4], q[3];
cx q[1], q[2];

cx q[2], q[3]; //swap 2 3
cx q[3], q[2]; //swap 2 3
cx q[2], q[3]; //swap 2 3
// 0->2, 1->1, 2->3, 3->4
cx q[2], q[1];
cx q[3], q[4];
tdg q[2];
tdg q[1];
tdg q[3];
t q[4];
cx q[2], q[1];
cx q[3], q[4];
s q[4];
cx q[4], q[2];
h q[4];
measure q[2]->c[0];
measure q[1]->c[1];
measure q[3]->c[2];
measure q[4]->c[3];
