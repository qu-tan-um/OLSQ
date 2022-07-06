OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
creg c[4];
cx q[2],q[3];
cx q[1],q[2];
u1(-0.7853981633974483) q[1];
u1(0.7853981633974483) q[2];
cx q[1],q[2];
u1(1.5707963267948966) q[2];
cx q[3],q[4];
u1(-0.7853981633974483) q[3];
u1(-0.7853981633974483) q[4];
cx q[3],q[4];
cx q[2],q[3];
u2(0,3.141592653589793) q[2];
cx q[1],q[2];
cx q[2],q[1];
cx q[1],q[2];
u2(0,3.141592653589793) q[1];
cx q[2],q[1];
u1(-0.7853981633974483) q[1];
u1(0.7853981633974483) q[2];
cx q[2],q[1];
u3(3.141592653589793,0,3.141592653589793) q[3];
u1(0.7853981633974483) q[3];
u3(3.141592653589793,0,3.141592653589793) q[4];
u1(0.7853981633974483) q[4];
cx q[3],q[4];
cx q[4],q[2];
measure q[3] -> c[0];
measure q[4] -> c[1];
measure q[1] -> c[2];
measure q[2] -> c[3];