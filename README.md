# OLSQ-GA

The results presented in the paper can be found in the `results` folder.
We used Python package `z3-solver 4.8.12.0`.
To run the experiments, refer to the help message of `iccad21.py`:
```
usage: iccad21.py [-h] [--size SIZE] [--matching] [--initmap]
                  [--filename FILENAME]
                  OBJ B

positional arguments:
  OBJ                  the objective: swap or depth
  B                    which input quantum circuit: qaoa, qv64, or sim5

optional arguments:
  -h, --help           show this help message and exit
  --size SIZE          The size of the qaoa circuit: 8, 10, 12, or 14
  --matching           if using alternating matchings
  --initmap            if setting initial mapping
  --filename FILENAME  The file name of the results (a json dump)
```
For example, to solve qv64 with depth as the objective, using alternating matchings,
setting initial mapping, and write the result to `qv64.json` at this directory, run
```bash
python3 iccad21.py --matching --initmap --filename=qv64 depth qv64
```
Below is a readme for the OLSQ pakcage for further understanding of the script.

## OLSQ: Optimal Layout Synthesis for Quantum Computing

[![iccad](https://img.shields.io/badge/Published-ICCAD'20-brightgreen.svg?style=for-the-badge)](https://ieeexplore.ieee.org/document/9256696)
[![arXiv](https://img.shields.io/badge/arXiv-2007.15671-brightgreen.svg?style=for-the-badge)](https://arxiv.org/abs/2007.15671)
[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

### Initialization

```python
from olsq import OLSQ

# initiate olsq with depth as objective, in normal mode
lsqc_solver = OLSQ("depth", "normal")
```

There are two argument in the constructor of OLSQ: `objective_name` and `mode`.
- `objective_name`: `"depth"`, `"swap"`, or `"fidelity"`.
- `mode`:  `"normal"` or `"transition"`.
The latter stands for TB-OLSQ in the paper, which is usually much faster with little loss of optimality.

### Setting the device

To perform LSQC, we need to know the connections between the qubits, which is information about the physical device.
We are going to use the `setdevice` method.
In general, there are three ways: 
1. Directly construct a device with some properties.
2. Use one of the hard-coded devices (including all the devices appeared in the paper).
3. Use device defined in other packages: refer to later parts of this tutorial on [Cirq](#cirq-interface) and [Qiskit](#qiskit-interface).

```python
from olsq.device import qcdevice

# directly construct a device from properties needed by olsq
lsqc_solver.setdevice( qcdevice(name="dev", nqubits=5, 
     connection=[(0, 1), (1, 2), (1, 3), (3, 4)], swap_duration=3) )
```

We use a minimalist class `qcdevice` to store the properties of the device that we need, which can be constructed with these arguments.
(The last three are only for fidelity optimization.)
- `name`
- `nqubits`: the number of physical qubits
- `connection`: a list of physical qubit pairs corresponding to edges in the coupling graph
- `swap_duration`: number of cycles a SWAP gate takes.
   Usually it is either one, or three meaning three CX gates.
- `fmeas`: a list of measurement fidelity
- `fsingle`: a list of single-qubit gate fidelity
- `ftwo`: a list of two-qubit gate fidelity, indices aligned with `connection`

If `name` starts with `"default_"`, a hard-coded device stored in `olsq/devices/` would be loaded.
Other arguments can still be specified, in which case the original device properties would be replaced by the input.
```python
# use a hard-coded device in olsq/devices/ called ourense
# which actually has the same properties as the device we constructed above
lsqc_solver.setdevice( qcdevice("default_ourense") )
```

### Setting the Input Program

Apart from the device, we need the quantum program/circuit to execute, which can be set with the `setprogram` method.
_To be safe, always set the device first and then the program._

OLSQ has an intermediate representation (IR) of quantum programs. (For details, refer to [a later part](#olsq-ir) of this tutorial.)
In general, there are four ways to set the program: 
1. Use OLSQ IR
2. Use a string in QASM format
3. Use an QASM file, e.g., one of programs used in the paper in `olsq/benchmarks/`.
4. Use programs defined in other packages: refer to later parts of this tutorial on [Cirq](#cirq-interface) and [Qiskit](#qiskit-interface).

```python
circuit_str = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[3];\nh q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\n" \
              "cx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[1];\nt q[2];\n" \
              "cx q[0], q[1];\nh q[2];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n"

# input the quantum program as a QASM string
lsqc_solver.setprogram(circuit_str)
```

The example above is a Toffoli gate.
We can also load an QASM file of it.
```python
# load one of the QASM files from olsq/benchmarks
lsqc_solver.setprogram("toffoli", input_mode="benchmark")

# load your own QASM file
# circuit_file = open("my-qasm-file", "r").read()

lsqc_solver.setprogram(circuit_file)

# Toffoli Gate:
#                                                        ┌───┐      
# q_0: ───────────────────■─────────────────────■────■───┤ T ├───■──
#                         │             ┌───┐   │  ┌─┴─┐┌┴───┴┐┌─┴─┐
# q_1: ───────■───────────┼─────────■───┤ T ├───┼──┤ X ├┤ TDG ├┤ X ├
#      ┌───┐┌─┴─┐┌─────┐┌─┴─┐┌───┐┌─┴─┐┌┴───┴┐┌─┴─┐├───┤└┬───┬┘└───┘
# q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├┤ T ├┤ X ├┤ TDG ├┤ X ├┤ T ├─┤ H ├──────
#      └───┘└───┘└─────┘└───┘└───┘└───┘└─────┘└───┘└───┘ └───┘      
```

### Solving and Output

It can be seen that in the Toffoli gate above, there are two-qubit gates on pair `(q_0,q_1)`, `(q_1,q_2)`, and `(q_2,q_0)`.
However, there are no such triangles on device `ourense`.
This means that no matter how the qubits in the program are mapped to physical qubits, we need to insert SWAP gates.

```python
# solve LSQC
result = lsqc_solver.solve()
```

The `solve` method can take two optional arguemnts
- `output_mode`: can be `"IR"`. Refer [here](#olsq-ir) on what would be returned in this case.
- `output_file_name`

If `output_mode` is default, the return is a tuple of three things:
- A string representing the output quantum program in QASM format.
If `output_file_name` is provided, then the QASM string would be written to that file.
- final_mapping: from each program qubit to the corresponding physical qubit at the end of execution.
- objective_value

The result of the Toffoli example is shown below.
Note that a SWAP gate, decomposed into three CX gates, has been inserted.
```python
# a LSQC solution to the Toffoli gate on device 'ourense'
#                                                  ┌───┐     ┌───┐┌───┐ ┌───┐      ┌─┐      
# q_0: ───────────────────■─────────────────────■──┤ X ├──■──┤ X ├┤ T ├─┤ H ├──────┤M├──────
#      ┌───┐┌───┐┌─────┐┌─┴─┐┌───┐┌───┐┌─────┐┌─┴─┐└─┬─┘┌─┴─┐└─┬─┘└───┘ ├───┤      └╥┘┌─┐   
# q_1: ┤ H ├┤ X ├┤ TDG ├┤ X ├┤ T ├┤ X ├┤ TDG ├┤ X ├──■──┤ X ├──■────■───┤ T ├───■───╫─┤M├───
#      └───┘└─┬─┘└─────┘└───┘└───┘└─┬─┘└┬───┬┘└───┘     └───┘     ┌─┴─┐┌┴───┴┐┌─┴─┐ ║ └╥┘┌─┐
# q_2: ───────■─────────────────────■───┤ T ├─────────────────────┤ X ├┤ TDG ├┤ X ├─╫──╫─┤M├
#                                       └───┘                     └───┘└─────┘└───┘ ║  ║ └╥┘
# q_3: ─────────────────────────────────────────────────────────────────────────────╫──╫──╫─
#                                                                                   ║  ║  ║
# q_4: ─────────────────────────────────────────────────────────────────────────────╫──╫──╫─
#                                                                                   ║  ║  ║
# c: 5/═════════════════════════════════════════════════════════════════════════════╩══╩══╩═
#                                                                                   2  0  1
```

### Cirq Interface

We can input a `networkx.Graph` object representing the devie to `setdevicegraph`.
Note that the method name is different from `setdevice`.
(Such a representation is used in some components in Cirq, e.g.,`device_graph` on [this line](https://github.com/quantumlib/Cirq/blob/8f9d8597364b8bd0d29833cbbd014ebf1c62f3db/cirq/contrib/quantum_volume/quantum_volume.py#L215).)

We can input a `cirq.Circuit` object as program in `setprogram`.
```python
from olsq.olsq_cirq import OLSQ_cirq

lsqc_solver = OLSQ_cirq("depth", "normal")

# use a cirq.Circuit object as program
lsqc_solver.setprogram(circuit)

# use a networkx.Graph object representing the device
lsqc_solver.setdevicegraph(device_graph)

# result_circuit is a cirq.Circuit object
result_circuit, final_mapping, objective_value = lsqc_solver.solve()
```
### Qiskit Interface

A `backend` from `IBMQ` can be input to the `setdevice` method with the second argument set to `"ibm"`.

There are two arguments for the `setprogram` method of `OLSQ_qiskit`: if the second is `"qasm"`, input a QASM string representing the quantum program as the first argument; if the second is none, then input a `QuantumCircuit` object in Qiskit as the first argument.

```python
from qiskit import IBMQ
from olsq.olsq_qiskit import OLSQ_qiskit

lsqc_solver = OLSQ_qiskit("depth", "normal")

# use a qiskit.QuantumCircuit object as program
lsqc_solver.setprogram(circuit)

provider = IBMQ.load_account()
backend = provider.get_backend("ibmq_lima") # change to your backend of choice
# use an IBMQ backend as the device
lsqc_solver.setdevice(backend, "ibm")

# result_circuit is a qiskit.QuantumCircuit object
result_circuit, final_mapping, objective_value = lsqc_solver.solve()
```

### TB-OLSQ

The transition-based mode is enabled if chosen at the initiation of `OLSQ`.
Roughly speaking, we only use a kind of coarse-grain time in this mode, so the runtime is much shorter.
For theoretical details, please refer to [the paper](https://doi.org/10.1145/3400302.3415620).
The returned QASM string and `final_mapping` should be similar to what they were before.
Only if the objective is `"depth"`, the objective value would be very different from the normal mode.
There is only one SWAP inserted, so there are only two coarse-grain time steps, separated by the SWAP, whereas there are 14 time steps if using exact time.

### OLSQ IR

OLSQ IR contains three things:
1. `count_program_qubit`: the number of qubits in the program.
2. `gates`: a list of tuples representing qubit(s) acted on by a gate, each tuple has one index if it is a single-qubit gate, two indices if it is a two-qubit gate.
3. `gate_spec`: list of type/name of each gate, which is not important to OLSQ, and only needed when generating output.

```python
# For the following circuit
# q_0: ───────────────────■───
#                         │  
# q_1: ───────■───────────┼───
#      ┌───┐┌─┴─┐┌─────┐┌─┴─┐
# q_2: ┤ H ├┤ X ├┤ TDG ├┤ X ├─
#      └───┘└───┘└─────┘└───┘ 

# count_program_qubit = 3
# gates = ((2,), (1,2), (2,), (0,1))
# gate_spec = ("h", "cx", "tdg", "cx")
```

If in the `solve` method, `output_mode` is set to `"IR"`, the return is a tuple of five things
1. `result_depth`: depth of the resulting quantum program
2. `list_scheduled_gate_name`: similar to `gate_spec` in the IR
3. `list_scheduled_gate_qubits`: similar to `gates` in the IR
4. `final_mapping`
5. `objective_value`

### BibTeX Citation
```
@InProceedings{iccad20-tan-cong-optimal-layout-synthesis,
  author          = {Tan, Bochen and Cong, Jason},
  booktitle       = {Proceedings of the 39th International Conference on Computer-Aided Design},
  title           = {Optimal Layout Synthesis for Quantum Computing},
  year            = {2020},
  address         = {New York, NY, USA},
  publisher       = {Association for Computing Machinery},
  series          = {ICCAD '20},
  archiveprefix   = {arXiv},
  eprint          = {2007.15671},
  primaryclass    = {quant-ph},
  articleno       = {137},
  doi             = {10.1145/3400302.3415620},
  isbn            = {9781450380263},
  keywords        = {quantum computing, scheduling, allocation, mapping, placement, layout synthesis},
  location        = {Virtual Event, USA},
  numpages        = {9},
  url             = {https://doi.org/10.1145/3400302.3415620},
}
```
