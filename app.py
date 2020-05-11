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

from flask import Flask, jsonify, abort, make_response, request
import implementation_handler
from qiskit import IBMQ, transpile, assemble
import json

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


@app.route('/qiskit-service/api/v1.0/transpile', methods=['POST'])
def transpile_circuit():
    """Get implementation from URL. Pass input into implementation. Generate circuit and return depth and width."""
    if not request.json or not 'impl-url' in request.json or not 'qpu-name' in request.json:
        abort(400)
    impl_url = request.json['impl-url']
    print(impl_url)
    qpu_name = request.json['qpu-name']
    input_params = request.json.get('input-params', "")
    print(input_params)

    circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
    print(circuit)

    IBMQ.load_account()
    provider = IBMQ.get_provider(group='open')
    backend = provider.get_backend(qpu_name)
    transpiled_circuit = transpile(circuit, backend=backend)

    depth = transpiled_circuit.depth()
    width = transpiled_circuit.width()

    return jsonify({'depth': depth}, {'width': width})


@app.route('/qiskit-service/api/v1.0/execute', methods=['POST'])
def execute_circuit():
    """Get implementation from URL. Pass input into implementation. Generate circuit. Run circuit on IBMQ.
     Return content location with results."""
    if not request.json or not 'impl-url' in request.json or not 'qpu-name' in request.json \
            or not 'token' in request.json:
        abort(400)
    impl_url = request.json['impl-url']
    qpu_name = request.json['qpu-name']
    token = request.json['token']
    input_params = request.json.get('input-params', "")
    shots = request.json.get('shots', "1024")

    circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)

    IBMQ.save_account(token, overwrite=True)
    IBMQ.load_account()
    provider = IBMQ.get_provider(group='open')
    backend = provider.get_backend(qpu_name)

    transpiled_circuit = transpile(circuit, backend=backend)

    qobj = assemble(transpiled_circuit, shots=shots)
    qobj_dict = qobj.to_dict()
    data_dict = {'qObject': qobj_dict, 'backend': {'name': qpu_name}}
    data = json.dumps(data_dict)
    print(data)

    return jsonify({'create_qobj': 'worked'})


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Internal Server Error', 'statusCode': '500'}), 500)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'statusCode': '404'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request', 'statusCode': '400'}), 400)
