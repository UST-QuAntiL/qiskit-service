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

from app import app, ibmq_handler, implementation_handler, db, parameters
from app.result_model import Result
from flask import jsonify, abort, request
from qiskit import transpile
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

    if not request.json \
            or not 'qpu-name' in request.json \
            or not 'token' in request.json:
        abort(400)

    qpu_name = request.json['qpu-name']
    impl_language = request.json.get('impl-language', '')
    input_params = request.json.get('input-params', "")
    input_params = parameters.ParameterDictionary(input_params)
    if 'token' in input_params:
        token = input_params['token']
    elif 'token' in request.json:
        token = request.json.get('token')

    if 'impl-url' in request.json:
        impl_url = request.json['impl-url']
        if impl_language.lower() == 'qasm':
            short_impl_name = 'no name'
            circuit = implementation_handler.prepare_code_from_qasm_url(impl_url)
        else:
            short_impl_name = re.match(".*/(?P<file>.*\\.py)", impl_url).group('file')
            try:
                circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
            except ValueError:
                abort(400)

    elif 'impl-data' in request.json:
        impl_data = base64.b64decode(request.json.get('impl-data').encode()).decode()
        short_impl_name = 'no short name'
        if impl_language.lower() == 'qasm':
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
    return jsonify({'depth': depth, 'width': width, 'transpiled_qasm': transpiled_circuit.qasm()}), 200


@app.route('/qiskit-service/api/v1.0/execute', methods=['POST'])
def execute_circuit():
    """Put execution job in queue. Return location of the later result."""
    if not request.json or not 'impl-url' in request.json or not 'qpu-name' in request.json \
            or not 'token' in request.json:
        abort(400)
    impl_url = request.json['impl-url']
    qpu_name = request.json['qpu-name']
    input_params = request.json.get('input-params', "")
    input_params = parameters.ParameterDictionary(input_params)
    shots = request.json.get('shots', 1024)
    if 'token' in input_params:
        token = input_params['token']
    elif 'token' in request.json:
        token = request.json.get('token')


    job = app.execute_queue.enqueue('app.tasks.execute', impl_url=impl_url, qpu_name=qpu_name, token=token,
                                    input_params=input_params, shots=shots)
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


@app.route('/qiskit-service/api/v1.0/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """Return result when it is available."""
    result = Result.query.get(result_id)
    if result.complete:
        result_dict = json.loads(result.result)
        return jsonify({'id': result.id, 'complete': result.complete, 'result': result_dict}), 200
    else:
        return jsonify({'id': result.id, 'complete': result.complete}), 200


@app.route('/qiskit-service/api/v1.0/version', methods=['GET'])
def version():
    return jsonify({'version': '1.0'})
