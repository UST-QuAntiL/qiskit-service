# ******************************************************************************
#  Copyright (c) 2021 University of Stuttgart
#
#  See the NOTICE file(s) distributed with this work for additional
#  information regarding copyright ownership.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************

from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes import RemoveFinalMeasurements


def get_width_of_circuit(circuit):
    """Get number of qubits required by the circuit"""
    remove_final_meas = RemoveFinalMeasurements()
    active_qubits = [
        qubit for qubit in circuit.qubits if
        qubit not in remove_final_meas.run(circuit_to_dag(circuit)).idle_wires()
    ]
    return len(active_qubits)


def get_multi_qubit_gate_depth(transpiled_circuit):
    """Get multi qubit gate depth by constructing a set of all occurring nonlocal gates
    and iterating over all gates of the transpiled circuit checking if in set or not"""

    # construct set of names of occurring multi-qubit gates, i.e. nonlocal gates
    transpiled_dag = circuit_to_dag(transpiled_circuit)
    set_of_all_nonlocal_gates = set()
    for gate in transpiled_dag.multi_qubit_ops():
        set_of_all_nonlocal_gates.add(gate.name)
    for gate in transpiled_dag.two_qubit_ops():
        set_of_all_nonlocal_gates.add(gate.name)
    print(set_of_all_nonlocal_gates)

    # remove all single qubit gates
    # get all gates and check if they are single qubit gates
    circuit_for_getting_multi_qubit_gate_depth = transpiled_circuit
    i = 0
    for gate in list(circuit_for_getting_multi_qubit_gate_depth.data):
        gate_name = gate[0].name
        if gate_name not in set_of_all_nonlocal_gates:
            circuit_for_getting_multi_qubit_gate_depth.data.pop(i)
        else:
            # i is only incremented if the regarded gate (i.e. a nonlocal gate) is not removed,
            # thus, the list size did not changed and go ahead to the next index
            i = i + 1

    print("Multi Qubit Gate Depth Circuit")
    print(circuit_for_getting_multi_qubit_gate_depth)
    return circuit_for_getting_multi_qubit_gate_depth.depth()
