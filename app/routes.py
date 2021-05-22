# ******************************************************************************
#  Copyright (c) 2020 University of Stuttgart
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
from qiskit.circuit.random import random_circuit

from app import app, benchmarking, ibmq_handler, implementation_handler, db, parameters
from app.benchmark_model import Benchmark
from app.result_model import Result
from flask import jsonify, abort, request
from qiskit import transpile, IBMQ
from qiskit.transpiler.passes import RemoveFinalMeasurements
from qiskit.converters import circuit_to_dag
from qiskit.transpiler.exceptions import TranspilerError
import logging
import json
import re
import base64


@app.route('/qiskit-service/api/v1.0/transpile', methods=['POST'])
def transpile_circuit():
    """Get implementation from URL. Pass input into implementation. Generate and transpile circuit
    and return depth and width."""

    if not request.json or not 'qpu-name' in request.json:
        abort(400)

    qpu_name = request.json['qpu-name']
    impl_language = request.json.get('impl-language', '')
    input_params = request.json.get('input-params', "")
    impl_url = request.json.get('impl-url', "")
    input_params = parameters.ParameterDictionary(input_params)
    if 'token' in input_params:
        token = input_params['token']
    elif 'token' in request.json:
        token = request.json.get('token')
    else:
        abort(400)

    if impl_url is not None and impl_url != "":
        impl_url = request.json['impl-url']
        if impl_language.lower() == 'openqasm':
            short_impl_name = 'no name'
            circuit = implementation_handler.prepare_code_from_qasm_url(impl_url)
        else:
            short_impl_name = "untitled"
            try:
                circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
            except ValueError:
                abort(400)

    elif 'impl-data' in request.json:
        impl_data = base64.b64decode(request.json.get('impl-data').encode()).decode()
        short_impl_name = 'no short name'
        if impl_language.lower() == 'openqasm':
            circuit = implementation_handler.prepare_code_from_qasm(impl_data)
        else:
            try:
                circuit = implementation_handler.prepare_code_from_data(impl_data, input_params)
            except ValueError:
                abort(400)
    else:
        abort(400)

    try:
        print(circuit)
        remove_final_meas = RemoveFinalMeasurements()
        active_qubits = [
            qubit for qubit in circuit.qubits if
            qubit not in remove_final_meas.run(circuit_to_dag(circuit)).idle_wires()
        ]
        non_transpiled_width = len(active_qubits)
        non_transpiled_depth = circuit.depth()
        print(f"Non transpiled width {non_transpiled_width} & non transpiled depth {non_transpiled_depth}")
        if not circuit:
            app.logger.warn(f"{short_impl_name} not found.")
            abort(404)
    except Exception as e:

        app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: {str(e)}")
        return jsonify({'error': str(e)}), 200

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if not backend:
        # ibmq_handler.delete_token()
        app.logger.warn(f"{qpu_name} not found.")
        abort(404)

    try:
        transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
        remove_final_meas = RemoveFinalMeasurements()
        active_qubits = [
            qubit for qubit in transpiled_circuit.qubits if
            qubit not in remove_final_meas.run(circuit_to_dag(transpiled_circuit)).idle_wires()
        ]
        width = len(active_qubits)
        depth = transpiled_circuit.depth()
        print(f"Transpiled width {width} & transpiled depth {depth}")


    except TranspilerError:
        app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: too many qubits required")
        return jsonify({'error': 'too many qubits required'}), 200

    app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: w={width} d={depth}")
    return jsonify({'depth': depth, 'width': width, 'transpiled-qasm': transpiled_circuit.qasm()}), 200


@app.route('/qiskit-service/api/v1.0/execute', methods=['POST'])
def execute_circuit():
    """Put execution job in queue. Return location of the later result."""
    if not request.json or not 'qpu-name' in request.json:
        abort(400)
    qpu_name = request.json['qpu-name']
    impl_language = request.json.get('impl-language', '')
    impl_url = request.json.get('impl-url')
    impl_data = request.json.get('impl-data')
    transpiled_qasm = request.json.get('transpiled-qasm')
    input_params = request.json.get('input-params', "")
    input_params = parameters.ParameterDictionary(input_params)
    shots = request.json.get('shots', 1024)
    if 'token' in input_params:
        token = input_params['token']
    elif 'token' in request.json:
        token = request.json.get('token')
    else:
        abort(400)

    job = app.execute_queue.enqueue('app.tasks.execute', impl_url=impl_url, impl_data=impl_data,
                                    impl_language=impl_language, transpiled_qasm=transpiled_qasm, qpu_name=qpu_name,
                                    token=token, input_params=input_params, shots=shots)
    result = Result(id=job.get_id())
    db.session.add(result)
    db.session.commit()

    logging.info('Returning HTTP response to client...')
    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    response = jsonify({'Location': content_location})
    response.status_code = 202
    response.headers['Location'] = content_location
    return response


@app.route('/qiskit-service/api/v1.0/calculate-calibration-matrix', methods=['POST'])
def calculate_calibration_matrix():
    """Put calibration matrix calculation job in queue. Return location of the later result."""
    if not request.json or not 'qpu-name' in request.json or not 'token' in request.json:
        abort(400)
    qpu_name = request.json['qpu-name']
    token = request.json['token']
    shots = request.json.get('shots', 8192)

    job = app.execute_queue.enqueue('app.tasks.calculate_calibration_matrix', qpu_name=qpu_name, token=token,
                                    shots=shots)
    result = Result(id=job.get_id())
    db.session.add(result)
    db.session.commit()

    logging.info('Returning HTTP response to client...')
    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    response = jsonify({'Location': content_location})
    response.status_code = 202
    response.headers['Location'] = content_location
    return response


@app.route('/qiskit-service/api/v1.0/randomize', methods=['POST'])
def randomize():
    """Create randomized circuits of given properties to run benchmarks and return locations to their results"""
    if not request.json:
        abort(400)

    qpu_name = request.json['qpu-name']
    num_of_qubits = request.json['number_of_qubits']
    min_depth_of_circuit = request.json['min_depth_of_circuit']
    max_depth_of_circuit = request.json['max_depth_of_circuit']
    num_of_circuits = request.json['number_of_circuits']
    shots = request.json.get('shots', 1024)
    token = request.json['token']

    locations = benchmarking.randomize(qpu_name=qpu_name, num_of_qubits=num_of_qubits, shots=shots,
                                       min_depth_of_circuit=min_depth_of_circuit,
                                       max_depth_of_circuit=max_depth_of_circuit, num_of_circuits=num_of_circuits,
                                       token=token)

    return jsonify(locations)


@app.route('/qiskit-service/api/v1.0/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Return result when it is available."""
    result = Result.query.get(result_id)
    if result.complete:
        result_dict = json.loads(result.result)
        return jsonify({'id': result.id, 'complete': result.complete, 'result': result_dict}), 200
    else:
        return jsonify({'id': result.id, 'complete': result.complete}), 200


@app.route('/qiskit-service/api/v1.0/benchmarks/<benchmark_id>', methods=['GET'])
def get_benchmark(benchmark_id):
    """Return summary of benchmark when it is available. Includes result of both simulator and quantum computer if
    available """
    benchmark_sim = None
    benchmark_real = None
    # get the simulator's and quantum computer's result from the db
    for benchmark in Benchmark.query.filter(Benchmark.benchmark_id == benchmark_id):
        if json.loads(benchmark.backend) == 'ibmq_qasm_simulator':
            benchmark_sim = benchmark
        else:
            benchmark_real = benchmark
    # check which backend has finished execution and adapt response to that
    if (benchmark_sim is not None) and (benchmark_real is not None):
        if benchmark_sim.complete and benchmark_real.complete:
            if benchmark_sim.result == "" or benchmark_real.result == "":
                # one backend failed during the execution
                return json.dumps({'error': 'execution failed'})

            # both backends finished execution
            return jsonify([{'id': benchmark_sim.id, 'backend': json.loads(benchmark_sim.backend),
                             'counts': json.loads(benchmark_sim.counts),
                             'original_depth': benchmark_sim.original_depth,
                             'original_width': benchmark_sim.original_width,
                             'transpiled_depth': benchmark_sim.transpiled_depth,
                             'transpiled_width': benchmark_sim.transpiled_width,
                             'benchmark_id': benchmark_sim.benchmark_id, 'complete': benchmark_sim.complete,
                             'shots': benchmark_sim.shots
                             },
                            {'id': benchmark_real.id, 'backend': json.loads(benchmark_real.backend),
                             'counts': json.loads(benchmark_real.counts),
                             'original_depth': benchmark_real.original_depth,
                             'original_width': benchmark_real.original_width,
                             'transpiled_depth': benchmark_real.transpiled_depth,
                             'transpiled_width': benchmark_real.transpiled_width,
                             'benchmark_id': benchmark_real.benchmark_id, 'complete': benchmark_real.complete,
                             'shots': benchmark_real.shots
                             }]), 200

        elif benchmark_sim.complete and not benchmark_real.complete:
            if benchmark_sim.result == "":
                # execution on simulator failed
                return json.dumps({'error': 'execution failed'})

            # simulator finished execution, quantum computer not yet
            return jsonify(
                [{'id': benchmark_sim.id, 'backend': benchmark_sim.backend, 'counts': json.loads(benchmark_sim.counts),
                  'original_depth': benchmark_sim.original_depth, 'original_width': benchmark_sim.original_width,
                  'transpiled_depth': benchmark_sim.transpiled_depth,
                  'transpiled_width': benchmark_sim.transpiled_width,
                  'benchmark_id': benchmark_sim.benchmark_id, 'complete': benchmark_sim.complete,
                  'shots': benchmark_sim.shots
                  },
                 {'id': benchmark_real.id, 'complete': benchmark_real.complete}]), 200

        elif not benchmark_sim.complete and benchmark_real.complete:
            if benchmark_real.result == "":
                # execution on quantum computer failed
                return json.dumps({'error': 'execution failed'})

            # quantum computer finished execution, simulator not yet
            return jsonify([{'id': benchmark_sim.id, 'complete': benchmark_sim.complete},
                            {'id': benchmark_real.id, 'backend': benchmark_real.backend,
                             'counts': json.loads(benchmark_real.counts),
                             'original_depth': benchmark_real.original_depth,
                             'original_width': benchmark_real.original_width,
                             'transpiled_depth': benchmark_real.transpiled_depth,
                             'transpiled_width': benchmark_real.transpiled_width,
                             'benchmark_id': benchmark_real.benchmark_id, 'complete': benchmark_real.complete,
                             'shots': benchmark_real.shots
                             }]), 200
        else:
            # both backends did not finish execution yet
            return jsonify([{'id': benchmark_sim.id, 'complete': benchmark_sim.complete},
                            {'id': benchmark_real.id, 'complete': benchmark_real.complete}]), 200
    else:
        abort(404)


@app.route('/qiskit-service/api/v1.0/analysis', methods=['GET'])
def get_analysis():
    """Return analysis of all benchmarks saved in the database"""
    return jsonify(benchmarking.analyse())


@app.route('/qiskit-service/api/v1.0/version', methods=['GET'])
def version():
    return jsonify({'version': '1.0'})
