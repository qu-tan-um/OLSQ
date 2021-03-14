from olsq.solve import OLSQ
from olsq.olsq_qiskit.input import input_qiskit

from olsq.device import qcdevice


class OLSQ_qiskit(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        super().__init__(objective_name, if_transition_based)
        self.map_program_qubit_to = []
        self.map_to_cirq_qubit = []

    def setdevicegraph(self, device_graph):


    def setprogram(self, program_cirq=None, input_mode=None):


    def solve(self, output_mode=None, output_file_name=None):
        