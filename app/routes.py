# ******************************************************************************
#  Copyright (c) 2020-2021 University of Stuttgart
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
from qiskit.providers.ibmq import IBMQAccountError

from app import app, benchmarking, aws_handler, ibmq_handler, implementation_handler, db, parameters, circuit_analysis, analysis
from app.benchmark_model import Benchmark
from app.qpu_metrics import generate_deterministic_uuid, get_all_qpus_and_metrics_as_json_str
from app.result_model import Result
from flask import jsonify, abort, request
from qiskit import transpile
from qiskit.transpiler.exceptions import TranspilerError
import json
import base64


@app.route('/qiskit-service/api/v1.0/transpile', methods=['POST'])
def transpile_circuit():
    """Get implementation from URL. Pass input into implementation. Generate and transpile circuit
    and return depth and width."""

    if not request.json or not 'qpu-name' in request.json:
        abort(400)

    # Default value is ibmq for services that do not support multiple providers and expect the IBMQ provider
    provider = request.json.get('provider', 'ibmq')
    qpu_name = request.json['qpu-name']
    impl_language = request.json.get('impl-language', '')
    input_params = request.json.get('input-params', "")
    impl_url = request.json.get('impl-url', "")
    bearer_token = request.json.get("bearer-token", "")
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
            circuit = implementation_handler.prepare_code_from_qasm_url(impl_url, bearer_token)
        else:
            short_impl_name = "untitled"
            try:
                circuit = implementation_handler.prepare_code_from_url(impl_url, input_params, bearer_token)
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
    elif 'qasm-string' in request.json:
        short_impl_name = 'no short name'
        app.logger.info(request.json.get('qasm-string'))
        circuit = implementation_handler.prepare_code_from_qasm(request.json.get('qasm-string'))
    else:
        abort(400)

    try:
        print("circuit", circuit)
        non_transpiled_depth_old = 0
        non_transpiled_depth = circuit.depth()
        while non_transpiled_depth_old < non_transpiled_depth:
            non_transpiled_depth_old = non_transpiled_depth
            circuit = circuit.decompose()
            non_transpiled_depth = circuit.depth()
        non_transpiled_width = circuit_analysis.get_width_of_circuit(circuit)
        non_transpiled_total_number_of_operations = circuit.size()
        non_transpiled_number_of_multi_qubit_gates = circuit.num_nonlocal_gates()
        non_transpiled_number_of_measurement_operations = circuit_analysis.get_number_of_measurement_operations(circuit)
        non_transpiled_number_of_single_qubit_gates = non_transpiled_total_number_of_operations - \
                                       non_transpiled_number_of_multi_qubit_gates - \
                                       non_transpiled_number_of_measurement_operations
        non_transpiled_multi_qubit_gate_depth, non_transpiled_circuit = circuit_analysis.get_multi_qubit_gate_depth(circuit.copy())
        print(f"Non transpiled width {non_transpiled_width} & non transpiled depth {non_transpiled_depth}")
        if not circuit:
            app.logger.warn(f"{short_impl_name} not found.")
            abort(404)
    except Exception as e:

        app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: {str(e)}")
        return jsonify({'error': str(e)}), 200

    backend = None
    if provider == 'ibmq':
        credentials = {}
        if 'url' in input_params:
            credentials['url'] = input_params['url']
        if 'hub' in input_params:
            credentials['hub'] = input_params['hub']
        if 'group' in input_params:
            credentials['group'] = input_params['group']
        if 'project' in input_params:
            credentials['project'] = input_params['project']
        backend = ibmq_handler.get_qpu(token, qpu_name, **credentials)
    elif provider == 'aws':
        backend = aws_handler.get_qpu(qpu_name)
    if not backend:
        app.logger.warn(f"{qpu_name} not found.")
        abort(404)

    try:
        # TODO: Not sure whether this call will work for AWS?
        transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
        print("Transpiled Circuit")
        print(transpiled_circuit)
        width = circuit_analysis.get_width_of_circuit(transpiled_circuit)
        depth = transpiled_circuit.depth()
        total_number_of_operations = transpiled_circuit.size()
        number_of_multi_qubit_gates = transpiled_circuit.num_nonlocal_gates()
        number_of_measurement_operations = circuit_analysis.get_number_of_measurement_operations(transpiled_circuit)
        number_of_single_qubit_gates = total_number_of_operations - number_of_multi_qubit_gates - \
                                       number_of_measurement_operations
        multi_qubit_gate_depth, transpiled_circuit = circuit_analysis.get_multi_qubit_gate_depth(transpiled_circuit)
        print("After all")
        print(transpiled_circuit)

    except TranspilerError:
        app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: too many qubits required")
        return jsonify({'error': 'too many qubits required'}), 200

    app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: w={width}, "
                    f"d={depth}, "
                    f"multi qubit gate depth={multi_qubit_gate_depth}, "
                    f"total number of operations={total_number_of_operations}, "
                    f"number of single qubit gates={number_of_single_qubit_gates}, "
                    f"number of multi qubit gates={number_of_multi_qubit_gates}, "
                    f"number of measurement operations={number_of_measurement_operations}")
    return jsonify({'original-depth': non_transpiled_depth,
                    'original-width': non_transpiled_width,
                    'original-total-number-of-operations': non_transpiled_total_number_of_operations,
                    'original-number-of-multi-qubit-gates': non_transpiled_number_of_multi_qubit_gates,
                    'original-number-of-measurement-operations': non_transpiled_number_of_measurement_operations,
                    'original-number-of-single-qubit-gates': non_transpiled_number_of_single_qubit_gates,
                    'original-multi-qubit-gate-depth': non_transpiled_multi_qubit_gate_depth,
                    'depth': depth,
                    'multi-qubit-gate-depth': multi_qubit_gate_depth,
                    'width': width,
                    'total-number-of-operations': total_number_of_operations,
                    'number-of-single-qubit-gates': number_of_single_qubit_gates,
                    'number-of-multi-qubit-gates': number_of_multi_qubit_gates,
                    'number-of-measurement-operations': number_of_measurement_operations,
                    'transpiled-qasm': transpiled_circuit.qasm()}), 200


@app.route('/qiskit-service/api/v1.0/analyze-original-circuit', methods=['POST'])
def analyze_original_circuit():

    if not request.json:
        abort(400)

    impl_language = request.json.get('impl-language', '')
    impl_url = request.json.get('impl-url', "")
    input_params = request.json.get('input-params', "")
    bearer_token = request.json.get("bearer-token", "")
    input_params = parameters.ParameterDictionary(input_params)

    if impl_url is not None and impl_url != "":
        impl_url = request.json['impl-url']
        if impl_language.lower() == 'openqasm':
            short_impl_name = 'no name'
            circuit = implementation_handler.prepare_code_from_qasm_url(impl_url, bearer_token)
        else:
            short_impl_name = "untitled"
            try:
                circuit = implementation_handler.prepare_code_from_url(impl_url, input_params, bearer_token)
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
    elif 'qasm-string' in request.json:
        short_impl_name = 'no short name'
        app.logger.info(request.json.get('qasm-string'))
        circuit = implementation_handler.prepare_code_from_qasm(request.json.get('qasm-string'))
    else:
        abort(400)

    try:
        non_transpiled_depth_old = 0
        non_transpiled_depth = circuit.depth()
        while non_transpiled_depth_old < non_transpiled_depth:
            non_transpiled_depth_old = non_transpiled_depth
            circuit = circuit.decompose()
            non_transpiled_depth = circuit.depth()
        non_transpiled_width = circuit_analysis.get_width_of_circuit(circuit)
        non_transpiled_total_number_of_operations = circuit.size()
        non_transpiled_number_of_multi_qubit_gates = circuit.num_nonlocal_gates()
        non_transpiled_number_of_measurement_operations = circuit_analysis.get_number_of_measurement_operations(circuit)
        non_transpiled_number_of_single_qubit_gates = non_transpiled_total_number_of_operations - \
                                       non_transpiled_number_of_multi_qubit_gates - \
                                       non_transpiled_number_of_measurement_operations
        non_transpiled_multi_qubit_gate_depth, non_transpiled_circuit = circuit_analysis.get_multi_qubit_gate_depth(circuit)
        print(circuit)
        print(f"Non transpiled width {non_transpiled_width} & non transpiled depth {non_transpiled_depth}")
        if not circuit:
            app.logger.warn(f"{short_impl_name} not found.")
            abort(404)
    except Exception as e:
        return jsonify({'error': str(e)}), 200

    return jsonify({'original-depth': non_transpiled_depth,
                    'original-width': non_transpiled_width,
                    'original-total-number-of-operations': non_transpiled_total_number_of_operations,
                    'original-number-of-multi-qubit-gates': non_transpiled_number_of_multi_qubit_gates,
                    'original-number-of-measurement-operations': non_transpiled_number_of_measurement_operations,
                    'original-number-of-single-qubit-gates': non_transpiled_number_of_single_qubit_gates,
                    'original-multi-qubit-gate-depth': non_transpiled_multi_qubit_gate_depth}), 200


@app.route('/qiskit-service/api/v1.0/execute', methods=['POST'])
def execute_circuit():
    """Put execution jobs in queue. Return location of the later results."""
    if not request.json or not 'qpu-name' in request.json:
        abort(400)

    # Default value is ibmq for services that do not support multiple providers and expect the IBMQ provider
    provider = request.json.get('provider', 'ibmq')
    qpu_name = request.json['qpu-name']
    impl_language = request.json.get('impl-language', '')
    impl_url = request.json.get('impl-url')
    if type(impl_url) is str:
        impl_url = [impl_url]
    impl_data = request.json.get('impl-data')
    if type(impl_data) is str:
        impl_data = [impl_data]
    qasm_string = request.json.get('qasm-string')
    if type(qasm_string) is str:
        qasm_string = [qasm_string]

    transpiled_qasm = request.json.get('transpiled-qasm')
    if type(transpiled_qasm) is str:
        transpiled_qasm = [transpiled_qasm]
    bearer_token = request.json.get("bearer-token", "")
    input_params = request.json.get('input-params', "")
    noise_model = request.json.get("noise-model")
    only_measurement_errors = request.json.get("only-measurement-errors")
    optimization_level = request.json.get('transpilation-optimization-level', 3)
    input_params = parameters.ParameterDictionary(input_params)

    # Check parameters required for using premium accounts, de.imbq and reservations
    credentials = {}
    if 'url' in input_params:
        credentials['url'] = input_params['url']
    if 'hub' in input_params:
        credentials['hub'] = input_params['hub']
    if 'group' in input_params:
        credentials['group'] = input_params['group']
    if 'project' in input_params:
        credentials['project'] = input_params['project']

    shots = request.json.get('shots', 1024)
    if 'token' in input_params:
        token = input_params['token']
    elif 'token' in request.json:
        token = request.json.get('token')
    else:
        abort(400)

    job = app.execute_queue.enqueue('app.tasks.execute', provider=provider, impl_url=impl_url, impl_data=impl_data,
                                    impl_language=impl_language, transpiled_qasm=transpiled_qasm, qpu_name=qpu_name,
                                    token=token, input_params=input_params, noise_model=noise_model,
                                    only_measurement_errors=only_measurement_errors,
                                    optimization_level=optimization_level, shots=shots, bearer_token=bearer_token,
                                    qasm_string=qasm_string, **credentials)

    result = Result(id=job.get_id(), backend=qpu_name, shots=shots)
    db.session.add(result)
    db.session.commit()

    app.logger.info('Returning HTTP response to client...')
    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    response = jsonify({'Location': content_location})
    response.status_code = 202
    response.headers['Location'] = content_location
    response.autocorrect_location_header = True
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

    app.logger.info('Returning HTTP response to client...')
    content_location = '/qiskit-service/api/v1.0/results/' + result.id
    response = jsonify({'Location': content_location})
    response.status_code = 202
    response.headers['Location'] = content_location
    response.autocorrect_location_header = True
    return response


@app.route('/qiskit-service/api/v1.0/calc-wd/<qpu_name>', methods=['GET'])
def calc_wd(qpu_name):
    """calculates wd-value of a given Quantum Computer based on the clifford data in your database and returns it"""
    wd = benchmarking.calc_wd(qpu_name)
    return jsonify(wd)


# TODO: after Qiskit ignis is deprecated, the generation of Clifford gate circuits has to be adapted
# @app.route('/qiskit-service/api/v1.0/randomize', methods=['POST'])
# def randomize():
#     """Create randomized circuits of given properties to run benchmarks and return locations to their results"""
#     if not request.json:
#         abort(400)
#
#     qpu_name = request.json['qpu-name']
#     num_of_qubits = request.json['number-of-qubits']
#     min_depth_of_circuit = request.json['min-depth-of-circuit']
#     max_depth_of_circuit = request.json['max-depth-of-circuit']
#     num_of_circuits = request.json['number-of-circuits']
#     clifford = request.json.get('clifford', False)
#     shots = request.json.get('shots', 1024)
#     token = request.json['token']
#
#     locations = benchmarking.randomize(qpu_name=qpu_name, num_of_qubits=num_of_qubits, shots=shots,
#                                        min_depth_of_circuit=min_depth_of_circuit,
#                                        max_depth_of_circuit=max_depth_of_circuit, num_of_circuits=num_of_circuits,
#                                        clifford=clifford, token=token)
#
#     return jsonify(locations)


@app.route('/qiskit-service/api/v1.0/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Return result when it is available."""
    result = Result.query.get(result_id)
    if result.complete:
        result_dict = json.loads(result.result)
        return jsonify({'id': result.id, 'complete': result.complete, 'result': result_dict,
                        'backend': result.backend, 'shots': result.shots}), 200
    else:
        return jsonify({'id': result.id, 'complete': result.complete}), 200


@app.route('/qiskit-service/api/v1.0/benchmarks/<benchmark_id>', methods=['GET'])
def get_benchmark(benchmark_id):
    """Return summary of benchmark when it is available. Includes result of both simulator and quantum computer if
    available """
    benchmark_sim = None
    benchmark_real = None
    # get the simulator's and quantum computer's result from the db
    i = 1  # for testing simulator can be benchmarked
    for benchmark in Benchmark.query.filter(Benchmark.benchmark_id == benchmark_id):
        if benchmark.backend == 'ibmq_qasm_simulator' and i > 0:
            benchmark_sim = benchmark
            i = i - 1
        else:
            benchmark_real = benchmark
    # check which backend has finished execution and adapt response to that
    if (benchmark_sim is not None) and (benchmark_real is not None):
        if benchmark_sim.complete and benchmark_real.complete:
            if benchmark_sim.result == "" or benchmark_real.result == "":
                # one backend failed during the execution
                return json.dumps({'error': 'execution failed'})

            # both backends finished execution
            return jsonify({'id': int(benchmark_id),
                            'benchmarking-complete': True,
                            'histogram-intersection': analysis.calc_intersection(
                                json.loads(benchmark_sim.counts).copy(),
                                json.loads(benchmark_real.counts).copy(),
                                benchmark_real.shots),
                            'perc-error': analysis.calc_percentage_error(json.loads(benchmark_sim.counts),
                                                                         json.loads(benchmark_real.counts)),
                            'correlation': analysis.calc_correlation(json.loads(benchmark_sim.counts).copy(),
                                                                     json.loads(benchmark_real.counts).copy(),
                                                                     benchmark_real.shots),
                            'chi-square': analysis.calc_chi_square_distance(json.loads(benchmark_sim.counts).copy(),
                                                                            json.loads(benchmark_real.counts).copy()),
                            'benchmarking-results': [get_benchmark_body(benchmark_backend=benchmark_sim),
                                                     get_benchmark_body(benchmark_backend=benchmark_real)]}), 200

        elif benchmark_sim.complete and not benchmark_real.complete:
            if benchmark_sim.result == "":
                # execution on simulator failed
                return json.dumps({'error': 'execution failed'})

            # simulator finished execution, quantum computer not yet
            return jsonify({'id': int(benchmark_id),
                            'benchmarking-complete': False,
                            'benchmarking-results': [get_benchmark_body(benchmark_backend=benchmark_sim),
                                                     {'result-id': benchmark_real.id,
                                                      'complete': benchmark_real.complete}]}), 200

        elif not benchmark_sim.complete and benchmark_real.complete:
            if benchmark_real.result == "":
                # execution on quantum computer failed
                return json.dumps({'error': 'execution failed'})

            # quantum computer finished execution, simulator not yet
            return jsonify({'id': int(benchmark_id),
                            'benchmarking-complete': False,
                            'benchmarking-results': [{'result-id': benchmark_sim.id,
                                                      'complete': benchmark_sim.complete},
                                                     get_benchmark_body(benchmark_backend=benchmark_real)]}), 200
        else:
            # both backends did not finish execution yet
            return jsonify({'id': int(benchmark_id),
                            'benchmarking-complete': False,
                            'benchmarking-results': [{'result-id': benchmark_sim.id,
                                                      'complete': benchmark_sim.complete},
                                                     {'result-id': benchmark_real.id,
                                                      'complete': benchmark_real.complete}]}), 200
    else:
        abort(404)


@app.route('/qiskit-service/api/v1.0/providers', methods=['GET'])
def get_providers():
    """Return available providers."""
    return jsonify({
        "_embedded": {
            "providerDtoes": [
                {
                    "id": str(generate_deterministic_uuid("ibmq", "provider")),
                    "name": "ibmq",
                    "offeringURL": "https://quantum-computing.ibm.com/",
                },
                {
                    "id": str(generate_deterministic_uuid("aws", "provider")),
                    "name": "aws",
                    "offeringURL": "https://aws.amazon.com/braket/",
                }
            ]
        }
    }), 200


@app.route('/qiskit-service/api/v1.0/providers/<provider_id>/qpus', methods=['GET'])
def get_qpus_and_metrics_of_provider(provider_id: str):
    """Return qpus and metrics of the specified provider."""

    if 'token' not in request.headers:
        return jsonify({"message": "Error: token missing in request"}), 401

    token = request.headers.get('token')

    if provider_id == str(generate_deterministic_uuid("ibmq", "provider")):
        try:
            return get_all_qpus_and_metrics_as_json_str(token), 200
        except IBMQAccountError:
            return jsonify({"message": "the provided token is wrong"}), 401
    else:
        return jsonify({"message": "Error: unknown provider ID."}), 400


@app.route('/qiskit-service/api/v1.0/analysis', methods=['GET'])
def get_analysis():
    """Return analysis of all benchmarks saved in the database"""
    return jsonify(benchmarking.analyse())


@app.route('/qiskit-service/api/v1.0/analysis/<qpu_name>', methods=['GET'])
def get_analysis_qpu(qpu_name):
    """Return analysis of all benchmarks from a specific quantum computer saved in the database"""
    benchmarks = Benchmark.query.all()
    list = []
    for i in range(0, len(benchmarks), 2):
        if (benchmarks[i].complete and benchmarks[i + 1].complete) and \
                (benchmarks[i].benchmark_id == benchmarks[i + 1].benchmark_id) and \
                (benchmarks[i].result != "" and benchmarks[i + 1].result != "") and \
                (benchmarks[i + 1].backend == qpu_name):
            counts_sim = json.loads(benchmarks[i].counts)
            counts_real = json.loads(benchmarks[i + 1].counts)
            shots = benchmarks[i + 1].shots
            perc_error = analysis.calc_percentage_error(counts_sim, counts_real)
            correlation = analysis.calc_correlation(counts_sim.copy(), counts_real.copy(), shots)
            chi_square = analysis.calc_chi_square_distance(counts_sim.copy(), counts_real.copy())
            intersection = analysis.calc_intersection(counts_sim.copy(), counts_real.copy(), shots)
            list.append({'benchmark-' + str(benchmarks[i].benchmark_id): {
                'benchmark-location': '/qiskit-service/api/v1.0/benchmarks/' + str(benchmarks[i].benchmark_id),
                'counts-sim': counts_sim,
                'counts-real': counts_real,
                'percentage-error': perc_error,
                'chi-square': chi_square,
                'correlation': correlation,
                'histogram-intersection': intersection}
            })
    return jsonify(list)


@app.route('/qiskit-service/api/v1.0/version', methods=['GET'])
def version():
    return jsonify({'version': '1.0'})


def get_benchmark_body(benchmark_backend):
    return {'result-id': benchmark_backend.id,
            'result-location': '/qiskit-service/api/v1.0/results/' + benchmark_backend.id,
            'backend': benchmark_backend.backend,
            'counts': json.loads(benchmark_backend.counts),
            'original-depth': benchmark_backend.original_depth,
            'original-width': benchmark_backend.original_width,
            'original-number-of-multi-qubit-gates': benchmark_backend.original_number_of_multi_qubit_gates,
            'transpiled-depth': benchmark_backend.transpiled_depth,
            'transpiled-width': benchmark_backend.transpiled_width,
            'transpiled-number-of-multi-qubit-gates': benchmark_backend.transpiled_number_of_multi_qubit_gates,
            'clifford': benchmark_backend.clifford,
            'benchmark-id': benchmark_backend.benchmark_id,
            'complete': benchmark_backend.complete,
            'shots': benchmark_backend.shots
            }
