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
from qiskit.transpiler.exceptions import TranspilerError
import logging
import json
import re


@app.route('/qiskit-service/api/v1.0/transpile', methods=['POST'])
def transpile_circuit():
    """Get implementation from URL. Pass input into implementation. Generate and transpile circuit
    and return depth and width."""

    if not request.json or not 'impl-url' in request.json or not 'qpu-name' in request.json \
            or not 'token' in request.json:
        abort(400)

    impl_url = request.json['impl-url']
    qpu_name = request.json['qpu-name']
    input_params = request.json.get('input-params', "")
    input_params = parameters.ParameterDictionary(input_params)
    token = input_params['token']

    short_impl_name = re.match(".*/(?P<file>.*\\.py)", impl_url).group('file')

    try:
        circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
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
        transpiled_circuit = transpile(circuit, backend=backend)
        depth = transpiled_circuit.depth()
        width = transpiled_circuit.num_qubits   # transpiled_circuit.width() also counts number of classical bits

    except TranspilerError:
        app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: too many qubits required")
        return jsonify({'error': 'too many qubits required'}), 200

    app.logger.info(f"Transpile {short_impl_name} for {qpu_name}: w={width} d={depth}")
    return jsonify({'depth': depth, 'width': width}), 200


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

    token = input_params['token']

    job = app.execute_queue.enqueue('app.tasks.execute', impl_url=impl_url, qpu_name=qpu_name, token=token,
                                       input_params=input_params, shots=shots)
    result = Result(id=job.get_id())
    db.session.add(result)
    db.session.commit()

    logging.info('Returning HTTP response to client...')
    content_location = '/qiskit-service/api/v1.0/results/'+result.id
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
