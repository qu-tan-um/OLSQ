OPENQASM 2.0;
include "qelib1.inc";
qreg node[5];
creg c[5];
u2(0,3.141592653589793) node[0];
u2(0,3.141592653589793) node[1];
u2(0,3.141592653589793) node[2];
cx node[2],node[0];
u1(1.5710000000000002) node[0];
cx node[2],node[0];
cx node[0],node[1];
u1(1.5710000000000002) node[1];
cx node[0],node[1];
u2(2.356,0) node[0];
u2(2.356,0) node[2];
u2(0,3.141592653589793) node[3];
u2(0,3.141592653589793) node[4];
measure node[2] -> c[0];
cx node[2],node[3];
cx node[3],node[2];
cx node[2],node[3];
cx node[1],node[2];
u1(1.5710000000000002) node[2];
cx node[1],node[2];
u2(2.356,0) node[1];
cx node[2],node[4];
u1(1.5710000000000002) node[4];
cx node[2],node[4];
u2(2.356,0) node[2];
u2(2.356,0) node[4];
measure node[0] -> c[1];
measure node[1] -> c[2];
measure node[2] -> c[3];
measure node[4] -> c[4];