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
import random
import numpy as np
import qiskit.ignis.verification.randomized_benchmarking as rb
from qiskit import IBMQ

from qiskit import transpile
from qiskit.circuit.random import random_circuit
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.passes import RemoveFinalMeasurements

from app import app, db, ibmq_handler, analysis
from app.benchmark_model import Benchmark
from app.result_model import Result


def run(circuit, backend, token, shots, benchmark_id, original_depth, original_width,
        original_number_of_multi_qubit_gates, transpiled_depth, transpiled_width,
        transpiled_number_of_multi_qubit_gates, clifford):
    """Enqueue jobs for randomized circuits for the execution and create database entries"""
    qasm = circuit.qasm()
    job = app.execute_queue.enqueue('app.tasks.execute_benchmark', transpiled_qasm=qasm, qpu_name=backend, token=token,
                                    shots=shots)
    # save benchmark properties to db
    result = Result(id=job.get_id(), backend=backend, shots=shots)
    benchmark = Benchmark(id=job.get_id(),
                          backend=backend,
                          shots=shots,
                          original_depth=original_depth,
                          original_width=original_width,
                          original_number_of_multi_qubit_gates=original_number_of_multi_qubit_gates,
                          transpiled_depth=transpiled_depth,
                          transpiled_width=transpiled_width,
                          transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates,
                          clifford=clifford,
                          benchmark_id=benchmark_id)
    db.session.add(result)
    db.session.add(benchmark)
    db.session.commit()

    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    return content_location


def calc_wd(qpu_name):
    """calculates the wd-value of a Quantum Computer based on the clifford data in your database"""
    wd = []
    wd_count = np.zeros([7, 5])
    min_sample_size = 15
    wd_success_count = np.zeros([7, 5])
    min_histogram_intersection = 0.75
    benchmarks = Benchmark.query.all()
    for i in range(0, len(benchmarks)):
        if benchmarks[i].complete and benchmarks[i].result != "" and benchmarks[i].backend == qpu_name\
                and benchmarks[i].clifford:
            counts = json.loads(benchmarks[i].counts)
            depth = benchmarks[i].transpiled_depth
            depth_range = int(np.floor(depth / 5))
            if depth_range > 6:
                depth_range = 6
            width = benchmarks[i].transpiled_width - 1
            if wd_count[depth_range, width] < min_sample_size:
                wd_count[depth_range, width] += 1
                first_value = list(counts.values())[0]
                intersection = first_value/benchmarks[i].shots
                # benchmark is successful if histogram intersection is at least min_histogram_intersection
                if intersection >= min_histogram_intersection:
                    wd_success_count[depth_range, width] += 1

    data_count = wd_count.copy()
    width_array = np.array([1, 2, 3, 4, 5])
    depth_array = np.array([5, 10, 15, 20, 25, 30, 35])

    wd_matrix = np.outer(depth_array, width_array)
    wd_count[wd_count == 0] = 1
    prob = wd_success_count/wd_count

    # wd class is successful if at least 2 out of 3 benchmarks are successful
    successful = prob.copy()
    successful[successful >= 2 / 3] = 1
    successful[successful < 2 / 3] = 0

    wd2 = wd_matrix.copy()
    wd2[successful == 0] = 0

    for i in range(5):
        for j in range(7):
            if wd_matrix[j, i] != wd2[j, i]:
                wd2[wd2 >= wd_matrix[j, i]] = 0

    wd.append({'wd': str(wd2.max()),
               'data_count': str(data_count)})

    return wd


def randomize(qpu_name, num_of_qubits, shots, min_depth_of_circuit, max_depth_of_circuit, num_of_circuits, clifford,
              token):
    """Create randomized circuits with given properties and jobs to run them on IBM backends."""
    sim_name = 'ibmq_qasm_simulator'
    backend_sim = ibmq_handler.get_qpu(token, sim_name)
    backend_real = ibmq_handler.get_qpu(token, qpu_name)
    locations = []

    if clifford:
        provider = IBMQ.get_provider(group='open')
        backend_real = provider.get_backend(qpu_name)
        backend_sim = provider.get_backend(sim_name)
        nseeds = num_of_circuits

        # random rb_pattern with random number of multi-qubit-gates
        qubit_seq = [j for j in range(num_of_qubits)]
        rb_pattern = []
        random.shuffle(qubit_seq)
        while qubit_seq:
            n = random.randint(1, len(qubit_seq))
            rb_pattern.append(qubit_seq[0:n])
            del qubit_seq[0:n]

        nCliffs = [random.randint(min_depth_of_circuit, max_depth_of_circuit) for _ in range(num_of_circuits)]
        rb_opts = {}
        rb_opts['length_vector'] = nCliffs
        rb_opts['nseeds'] = nseeds
        rb_opts['rb_pattern'] = rb_pattern

        rb_circs, xdata = rb.randomized_benchmarking_seq(**rb_opts)
        count = 0
        index_list_elem = 0

        for listElem in rb_circs:
            index_list_elem += 1
            count += len(listElem)
            for indexElem, elem in enumerate(listElem):
                rowcount = db.session.query(Benchmark).count()
                benchmark_id = rowcount // 2

                remove_final_meas = RemoveFinalMeasurements()

                transpiled_circuit_real = transpile(elem, backend=backend_real, optimization_level=3)
                transpiled_circuit_sim = transpile(elem, backend=backend_sim, optimization_level=3)

                active_qubits_transpiled_circuit_real = [
                    qubit for qubit in transpiled_circuit_real.qubits if
                    qubit not in remove_final_meas.run(circuit_to_dag(transpiled_circuit_real)).idle_wires()]
                active_qubits_transpiled_circuit_sim = [
                    qubit for qubit in transpiled_circuit_sim.qubits if
                    qubit not in remove_final_meas.run(circuit_to_dag(transpiled_circuit_sim)).idle_wires()]

                transpiled_depth_real = transpiled_circuit_real.depth()
                transpiled_number_of_multi_qubit_gates_real = transpiled_circuit_real.num_nonlocal_gates()
                transpiled_width_real = len(active_qubits_transpiled_circuit_real)
                # transpiled_number_of_multi_qubit_gates_real = qcircuit_real.num_nonlocal_gates()

                transpiled_depth_sim = transpiled_circuit_sim.depth()
                transpiled_number_of_multi_qubit_gates_sim = transpiled_circuit_sim.num_nonlocal_gates()
                transpiled_width_sim = len(active_qubits_transpiled_circuit_sim)
                # transpiled_number_of_multi_qubit_gates_sim = qcircuit_sim.num_nonlocal_gates()

                location_sim = run(circuit=transpiled_circuit_sim, backend=sim_name, token=token, shots=shots,
                                   benchmark_id=benchmark_id, original_depth=elem.depth(), original_width=num_of_qubits,
                                   original_number_of_multi_qubit_gates=elem.num_nonlocal_gates(),
                                   transpiled_depth=transpiled_depth_sim, transpiled_width=transpiled_width_sim,
                                   transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_sim,
                                   clifford=clifford)

                location_real = run(circuit=transpiled_circuit_real, backend=qpu_name, token=token, shots=shots,
                                    benchmark_id=benchmark_id,
                                    original_depth=elem.depth(), original_width=num_of_qubits,
                                    original_number_of_multi_qubit_gates=elem.num_nonlocal_gates(),
                                    transpiled_depth=transpiled_depth_real, transpiled_width=transpiled_width_real,
                                    transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_real,
                                    clifford=clifford)

                location_benchmark = '/qiskit-service/api/v1.0/benchmarks/' + str(benchmark_id)
                locations.append({'result-simulator': str(location_sim),
                                  'result-real-backend': str(location_real),
                                  'result-benchmark': str(location_benchmark)})
    else:
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
                                   transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_sim,
                                   clifford=clifford)

                location_real = run(circuit=qcircuit_real, backend=qpu_name, token=token, shots=shots,
                                    benchmark_id=benchmark_id,
                                    original_depth=i, original_width=num_of_qubits,
                                    original_number_of_multi_qubit_gates=original_number_of_multi_qubit_gates,
                                    transpiled_depth=transpiled_depth_real, transpiled_width=transpiled_width_real,
                                    transpiled_number_of_multi_qubit_gates=transpiled_number_of_multi_qubit_gates_real,
                                    clifford=clifford)
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
            list.append({'benchmark-' + str(benchmarks[i].benchmark_id): {
                'benchmark-location': '/qiskit-service/api/v1.0/benchmarks/' + str(benchmarks[i].benchmark_id),
                'counts-sim': counts_sim,
                # "Expected Value Sim": exp_value_sim,
                # "Standard Deviation Sim": sd_sim,
                'counts-real': counts_real,
                # "Expected Value Real": exp_value_real,
                # "Standard Deviation Real": sd_real,
                'percentage-error': perc_error,
                'chi-square': chi_square,
                'correlation': correlation,
                'histogram-intersection': intersection}
            })
    return list
