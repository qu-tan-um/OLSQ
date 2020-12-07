from olsq.solve import OLSQ
import cirq


class OLSQ_cirq(OLSQ):
    def __init__(self, objective_name, if_transition_based):
        super().__init__(objective_name, if_transition_based)

    def setdevice(self, device=None):
        s=1

    def setprogram(self, program=None):
        s = 1
