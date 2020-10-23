import pytket
from pytket.routing import Architecture, route
from pytket.qiskit import tk_to_qiskit
from pytket.qasm import circuit_from_qasm, circuit_to_qasm
from pytket.transform import Transform
from pytket.passes import DecomposeSwapsToCXs
from device import qcdevice
from info import qiskit_info_after, qiskit_info_original
from pytket.device import Device
from pytket.predicates import CompilationUnit
from pytket.passes import DecomposeSwapsToCXs
from qiskit import QuantumCircuit
import sys


def tket_run(file_name, device_name):
    connection_list = qcdevice(device_name).connection_list
    circ = circuit_from_qasm(file_name)
    circ.measure_all()
    arc = Architecture(connection_list)
    dev = Device(arc)
    routed_circ = route(circ, arc)
    # cu = CompilationUnit(routed_circ)
    Transform.DecomposeBRIDGE().apply(routed_circ)
    # pass1 = DecomposeSwapsToCXs(dev)
    # pass1.apply(cu)
    # circ2 = cu.circuit
    return routed_circ


file_name = sys.argv[1]
device_name = sys.argv[2]
new_file_name = "result/paper/" + file_name.split('/')[-1].replace('.qasm', "_{}_tket".format(device_name))

original_cx_count = qiskit_info_original(file_name, new_file_name)[1]


routed_circ = tket_run(file_name, device_name)
# circuit_to_qasm(circ, "result/paper/" + file_name.split('/')[-1] + "_tket.qasm")
circ = tk_to_qiskit(routed_circ)
qiskit_info_after(circ, new_file_name, original_cx_count)
