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

import json

from qiskit import transpile
from qiskit.circuit.random import random_circuit
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes import RemoveFinalMeasurements

from app import app, db, ibmq_handler, analysis
from app.benchmark_model import Benchmark
from app.result_model import Result


def run(circuit, backend, token, shots, benchmark_id, original_depth, original_width,
        original_number_of_multi_qubit_gates, transpiled_depth, transpiled_width,
        transpiled_number_of_multi_qubit_gates):
    """Enqueue jobs for randomized circuits for the execution and create database entries"""
    qasm = circuit.qasm()
    job = app.execute_queue.enqueue('app.tasks.execute_benchmark', transpiled_qasm=qasm, qpu_name=backend, token=token,
                                    shots=shots)
    # save benchmark properties to db
    result = Result(id=job.get_id())
    benchmark = Benchmark(id=job.get_id())
    db.session.add(result)
    db.session.add(benchmark)
    benchmark.shots = shots
    benchmark.backend = json.dumps(backend)
    benchmark.original_depth = original_depth
    benchmark.original_width = original_width
    benchmark.original_number_of_multi_qubit_gates = original_number_of_multi_qubit_gates
    benchmark.transpiled_depth = transpiled_depth
    benchmark.transpiled_width = transpiled_width
    benchmark.transpiled_number_of_multi_qubit_gates = transpiled_number_of_multi_qubit_gates
    benchmark.benchmark_id = benchmark_id
    db.session.commit()

    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    return content_location


def randomize(qpu_name, num_of_qubits, shots, min_depth_of_circuit, max_depth_of_circuit, num_of_circuits, token):
    """Create randomized circuits with given properties and jobs to run them on IBM backends."""
    sim_name = 'ibmq_qasm_simulator'
    backend_sim = ibmq_handler.get_qpu(token, sim_name)
    backend_real = ibmq_handler.get_qpu(token, qpu_name)
    locations = []

    # create the given number of circuits of given width and depth
    for i in range(min_depth_of_circuit, max_depth_of_circuit + 1):
        for j in range(num_of_circuits):
            rowcount = db.session.query(Benchmark).count()
            benchmark_id = rowcount // 2
            # create randomized circuits and transpile them for both backends
            qx = random_circuit(num_qubits=num_of_qubits, depth=i, measure=True)
            original_number_of_multi_qubit_gates = qx.num_nonlocal_gates()
            qcircuit_sim = transpile(qx, backend=backend_sim, optimization_level=3)
            qcircuit_real = transpile(qx, backend=backend_real, optimization_level=3)
            # ensure that the width of the circuit is correctly saved in the db
            remove_final_meas = RemoveFinalMeasurements()
            active_qubits_real = [
                qubit for qubit in qcircuit_real.qubits if
                qubit not in remove_final_meas.run(circuit_to_dag(qcircuit_real)).idle_wires()
            ]
            transpiled_depth_sim = qcircuit_sim.depth()
            transpiled_width_sim = qcircuit_sim.num_qubits
            transpiled_number_of_multi_qubit_gates_sim = qcircuit_sim.num_nonlocal_gates()
            transpiled_depth_real = qcircuit_real.depth()
            transpiled_width_real = len(active_qubits_real)
            transpiled_number_of_multi_qubit_gates_real = qcircuit_real.num_nonlocal_gates()

            location_sim = run(circuit=qcircuit_sim, backend=sim_name, token=token, shots=shots,
                               benchmark_id=benchmark_id,
                               original_depth=i, original_width=num_of_qubits,
                               original_number_of_multi_qubit_gates=original_number_of_multi_qubit_gates,
                               transpiled_depth=transpiled_depth_sim, transpiled_width=transpiled_width_sim,
                               transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_sim)

            location_real = run(circuit=qcircuit_real, backend=qpu_name, token=token, shots=shots,
                                benchmark_id=benchmark_id,
                                original_depth=i, original_width=num_of_qubits,
                                original_number_of_multi_qubit_gates=original_number_of_multi_qubit_gates,
                                transpiled_depth=transpiled_depth_real, transpiled_width=transpiled_width_real,
                                transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_real)
            location_benchmark = '/qiskit-service/api/v1.0/benchmarks/' + str(benchmark_id)
            locations.append({'result-simulator': str(location_sim),
                              'result-real-backend': str(location_real),
                              'result-benchmark': str(location_benchmark)})

    return locations


def analyse():
    """Analyse all benchmarks available in the database by the four metrics correlation, chi-square-distance,
    percentage error and histogram intersection. """
    benchmarks = Benchmark.query.all()
    list = []
    for i in range(0, len(benchmarks), 2):
        if (benchmarks[i].complete and benchmarks[i + 1].complete) and \
                (benchmarks[i].benchmark_id == benchmarks[i + 1].benchmark_id) and \
                (benchmarks[i].result != "" and benchmarks[i + 1].result != ""):
            counts_sim = json.loads(benchmarks[i].counts)
            counts_real = json.loads(benchmarks[i + 1].counts)
            # prb_sim and prb_real will contain the probability distribution of the result
            prb_sim = json.loads(benchmarks[i].counts)
            prb_real = json.loads(benchmarks[i + 1].counts)
            shots = benchmarks[i + 1].shots
            for key in prb_sim.keys():
                prb_sim[key] = prb_sim[key] / benchmarks[i].shots
                if key not in prb_real.keys():
                    prb_real[key] = 0
            for key in prb_real:
                prb_real[key] = prb_real[key] / benchmarks[i + 1].shots
                if key not in prb_sim.keys():
                    prb_sim[key] = 0

            # create a list of the analysis of all benchmarks as response
            # expected value and standard deviation are currently not used

            # exp_value_sim = analysis.calc_expected_value(prb_sim)
            # exp_value_real = analysis.calc_expected_value(prb_real)
            # sd_sim = analysis.calc_standard_deviation(prb_sim, exp_value_sim)
            # sd_real = analysis.calc_standard_deviation(prb_real, exp_value_real)

            perc_error = analysis.calc_percentage_error(counts_sim, counts_real)
            correlation = analysis.calc_correlation(counts_sim.copy(), counts_real.copy(), shots)
            chi_square = analysis.calc_chi_square_distance(counts_sim.copy(), counts_real.copy())
            intersection = analysis.calc_intersection(counts_sim.copy(), counts_real.copy(), shots)
            list.append({"benchmark-" + str(benchmarks[i].benchmark_id): {
                "transpiled-depth": benchmarks[i + 1].transpiled_depth,
                "transpiled-width": benchmarks[i + 1].transpiled_width,
                "transpiled-number-of-multi-qubit-gates": benchmarks[i + 1].transpiled_number_of_multi_qubit_gates,
                "counts-sim": counts_sim,
                # "Expected Value Sim": exp_value_sim,
                # "Standard Deviation Sim": sd_sim,
                "counts-real": counts_real,
                # "Expected Value Real": exp_value_real,
                # "Standard Deviation Real": sd_real,
                "percentage-error": perc_error,
                "chi-square": chi_square,
                "correlation": correlation,
                "intersection": intersection}
            })
    return list
